"""
tests/test_api.py
==================
Integration tests for the FastAPI /api/v1 routes.

Uses httpx.AsyncClient with the FastAPI TestClient pattern.
The DB is an in-memory SQLite instance (not the real DB).
The semantic model is mocked to avoid downloading ~500MB.

Verifies:
  1. GET /health → {status: "ok"}
  2. POST /analyze → correct response structure with all evidence fields
  3. POST /analyze → run_id is returned
  4. POST /analyze → fusion_score is present (not null after M2)
  5. POST /analyze → fusion_weight_metadata is present (Non-Negotiable Rule 5)
  6. POST /analyze → evidence lists are non-empty (Non-Negotiable Rule 2)
  7. POST /analyze → behavioral_evidence notes absence (not 0.0)
  8. POST /feedback/{run_id} → 200 ok for valid verdicts
  9. POST /feedback/{run_id} → 404 for unknown run_id
 10. GET /runs → returns list (may be empty)
 11. GET /fusion/weights → returns weights dict
 12. POST /analyze → file size limit enforced (>1MB rejected)
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.rate_limiter import limiter
from app.auth.security import create_access_token
from app.db.models import Base, User
from app.db.session import get_db_dependency
from app.main import app

FIXTURES = Path(__file__).parent / "fixtures"

# ──────────────────────────────────────────────────────────────────────────────
# In-memory SQLite DB fixture
# ──────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_db():
    """Create a fresh in-memory SQLite DB for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_dependency] = override_db
    limiter.reset()
    yield session_factory
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def instructor_token(test_db):
    """Helper fixture providing a valid user JWT token."""
    async with test_db() as session:
        user = User(
            username="user_api_test",
            email="user_api@ehsa.edu",
            password_hash="dummy_hash",
            role="user",
            is_active=1,
        )
        session.add(user)
        await session.commit()
        return create_access_token({"sub": user.id, "username": user.username, "role": user.role})


# ──────────────────────────────────────────────────────────────────────────────
# Mock semantic model (avoids ~500MB download in tests)
# ──────────────────────────────────────────────────────────────────────────────

def _mock_semantic():
    """Patch semantic_similarity to return (0.75, [evidence]) deterministically."""
    import app.api.routes as routes_module  # noqa: PLC0415

    def fake_semantic(code_a, code_b):
        return 0.75, [
            {
                "type": "cosine_similarity",
                "value": 0.75,
                "model": "mock-model",
                "token_count_a": 50,
                "token_count_b": 50,
                "note": "Mock semantic similarity.",
            },
            {
                "type": "truncation_disclosure",
                "file": "both",
                "note": "No truncation — mock.",
            },
        ]

    return patch.object(routes_module, "semantic_similarity", fake_semantic)


# ──────────────────────────────────────────────────────────────────────────────
# HTTP client fixture
# ──────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestHealth:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAnalyze:
    SIMPLE_CODE_A = "def add(a, b):\n    return a + b\n"
    SIMPLE_CODE_B = "def sum_two(x, y):\n    return x + y\n"

    @pytest.mark.asyncio
    async def test_analyze_returns_200(self, client):
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        assert response.status_code == 200, response.text

    @pytest.mark.asyncio
    async def test_analyze_returns_run_id(self, client):
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        assert "run_id" in data
        assert isinstance(data["run_id"], str)
        assert len(data["run_id"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_fusion_score_present(self, client):
        """After M2, fusion_score must be non-null."""
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        assert data["fusion_score"] is not None, "fusion_score must be present after M2"
        assert 0.0 <= data["fusion_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_weight_metadata_present(self, client):
        """Non-Negotiable Rule 5: fusion_weight_metadata must always be returned."""
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        assert data["fusion_weight_metadata"] is not None, \
            "fusion_weight_metadata must be present (Non-Negotiable Rule 5)"
        meta = data["fusion_weight_metadata"]
        assert "effective_weights" in meta
        assert "source" in meta
        assert "signals_used" in meta

    @pytest.mark.asyncio
    async def test_analyze_all_component_scores_present(self, client):
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        components = data["components"]
        assert "lexical" in components
        assert "structural" in components
        assert "semantic" in components
        assert "behavioral" in components  # None is acceptable — absence noted

    @pytest.mark.asyncio
    async def test_analyze_evidence_always_present(self, client):
        """Non-Negotiable Rule 2: every component must have a non-empty evidence list."""
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        components = data["components"]
        assert len(components["lexical_evidence"]) > 0, "lexical_evidence must not be empty"
        assert len(components["structural_evidence"]) > 0, "structural_evidence must not be empty"
        assert len(components["semantic_evidence"]) > 0, "semantic_evidence must not be empty"
        assert len(components["behavioral_evidence"]) > 0, \
            "behavioral_evidence must note its absence — not be empty"

    @pytest.mark.asyncio
    async def test_analyze_behavioral_evidence_notes_absence(self, client):
        """Behavioral is None but evidence must state it's absent, not silently 0."""
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        beh_ev = data["components"]["behavioral_evidence"]
        assert len(beh_ev) > 0
        # At least one evidence item should have a "note" about absence
        all_notes = " ".join(
            str(e.get("note", "")) for e in beh_ev
        ).lower()
        assert "not" in all_notes or "absent" in all_notes or "unavailable" in all_notes or \
               "implement" in all_notes, \
            "Behavioral evidence must explain why behavioral signal is absent"

    @pytest.mark.asyncio
    async def test_analyze_identical_code_high_lexical(self, client):
        code = Path(FIXTURES / "identical_a.py").read_text()
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={"submission_code": code, "reference_code": code},
            )
        data = response.json()
        assert data["components"]["lexical"] == pytest.approx(1.0)
        assert data["components"]["structural"] == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_analyze_file_size_limit_enforced(self, client):
        """Files >1MB must be rejected with 422."""
        big_code = "x = 1\n" * (200_000)  # ~1.2 MB
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={"submission_code": big_code, "reference_code": "x = 1"},
            )
        assert response.status_code == 422, \
            f"Expected 422 for oversized file, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_analyze_confidence_indicators_populated(self, client):
        """Section 9.3 & 10: confidence_indicators must be present with high/medium/low values."""
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        data = response.json()
        assert "confidence_indicators" in data
        assert data["confidence_indicators"] is not None
        conf = data["confidence_indicators"]
        for key in ["lexical", "structural", "semantic", "behavioral"]:
            assert key in conf
            assert conf[key] in {"high", "medium", "low"}

    @pytest.mark.asyncio
    async def test_analyze_ai_generation_evidence_persisted_to_db(self, client):
        """AGENTS.md & Section 11: ai_generation evidence must be persisted to the DB evidence table."""
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={
                    "submission_code": self.SIMPLE_CODE_A,
                    "reference_code": self.SIMPLE_CODE_B,
                },
            )
        run_id = r.json()["run_id"]
        report_resp = await client.get(f"/api/v1/report/{run_id}?format=json")
        data = report_resp.json()
        ai_ev = [e for e in data["evidence"] if e["dimension"] == "ai_generation"]
        assert len(ai_ev) > 0, "ai_generation evidence must be persisted to evidence DB table"

    @pytest.mark.asyncio
    async def test_analyze_syntax_error_code_handled(self, client):
        """Syntax error in submission must not crash the endpoint."""
        broken = "def broken(:\n    pass"
        with _mock_semantic():
            response = await client.post(
                "/api/v1/analyze",
                json={"submission_code": broken, "reference_code": "x = 1"},
            )
        assert response.status_code == 200, \
            f"Syntax error should not crash /analyze, got {response.status_code}"


class TestFeedback:
    @pytest.mark.asyncio
    async def test_feedback_confirmed_returns_ok(self, client, instructor_token):
        # First create a run
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 1"},
            )
        run_id = r.json()["run_id"]

        response = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "confirmed"},
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["verdict"] == "confirmed"

    @pytest.mark.asyncio
    async def test_feedback_false_positive_returns_ok(self, client, instructor_token):
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 1"},
            )
        run_id = r.json()["run_id"]
        response = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "false_positive"},
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_feedback_unknown_run_id_returns_404(self, client, instructor_token):
        response = await client.post(
            "/api/v1/feedback/nonexistent-run-id",
            json={"verdict": "confirmed"},
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_feedback_invalid_verdict_rejected(self, client, instructor_token):
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 1"},
            )
        run_id = r.json()["run_id"]
        response = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "invalid_verdict"},
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        assert response.status_code == 422


class TestRunsEndpoint:
    @pytest.mark.asyncio
    async def test_runs_returns_list(self, client, instructor_token):
        response = await client.get("/api/v1/runs", headers={"Authorization": f"Bearer {instructor_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "runs" in data
        assert isinstance(data["runs"], list)

    @pytest.mark.asyncio
    async def test_runs_shows_created_run(self, client, instructor_token):
        with _mock_semantic():
            await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 2"},
                headers={"Authorization": f"Bearer {instructor_token}"},
            )
        response = await client.get("/api/v1/runs", headers={"Authorization": f"Bearer {instructor_token}"})
        data = response.json()
        assert len(data["runs"]) >= 1


class TestFusionWeightsEndpoint:
    @pytest.mark.asyncio
    async def test_weights_returns_current(self, client):
        response = await client.get("/api/v1/fusion/weights")
        assert response.status_code == 200
        data = response.json()
        assert "current_weights" in data
        assert "source" in data
        weights = data["current_weights"]
        for key in ["lexical", "structural", "semantic", "behavioral"]:
            assert key in weights

class TestDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_dashboard_summary_returns_valid_structure(self, client, instructor_token):
        with _mock_semantic():
            await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 2"},
                headers={"Authorization": f"Bearer {instructor_token}"},
            )
        response = await client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {instructor_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total_runs" in data
        assert data["total_runs"] >= 1
        assert "flagged_count" in data
        assert "avg_fusion_score" in data
        assert "score_distribution" in data
        assert "transformation_breakdown" in data
        assert "weight_drift_history" in data
        assert "calibration_data" in data


class TestFusionWeightsEndpoint:
    @pytest.mark.asyncio
    async def test_weights_returns_current(self, client):
        response = await client.get("/api/v1/fusion/weights")
        assert response.status_code == 200
        data = response.json()
        assert "current_weights" in data
        assert "source" in data
        weights = data["current_weights"]
        for key in ["lexical", "structural", "semantic", "behavioral"]:
            assert key in weights

class TestBatchEndpoint:
    @pytest.mark.asyncio
    async def test_compare_batch_returns_matrix(self, client):
        with _mock_semantic():
            response = await client.post(
                "/api/v1/compare/batch",
                files=[
                    ("files", ("file1.py", b"x = 1")),
                    ("files", ("file2.py", b"x = 1")),
                    ("files", ("file3.py", b"x = 2")),
                ],
            )
        assert response.status_code == 200
        data = response.json()
        assert "matrix" in data
        matrix = data["matrix"]
        # N=3 -> 3*2/2 = 3 pairs
        assert len(matrix) == 3
        # Check structure
        for row in matrix:
            assert "run_id" in row
            assert "file_a" in row
            assert "file_b" in row
            assert "fusion_score" in row
            assert "transformation_type" in row

class TestReportEndpoint:
    @pytest.mark.asyncio
    async def test_report_json(self, client):
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 2"},
            )
        run_id = r.json()["run_id"]
        
        response = await client.get(f"/api/v1/report/{run_id}?format=json")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert f"ehsa_report_{run_id[:8]}.json" in response.headers["content-disposition"]
        data = response.json()
        assert data["run_id"] == run_id
        assert len(data["evidence"]) > 0

    @pytest.mark.asyncio
    async def test_report_html(self, client):
        with _mock_semantic():
            r = await client.post(
                "/api/v1/analyze",
                json={"submission_code": "x = 1", "reference_code": "y = 2"},
            )
        run_id = r.json()["run_id"]
        
        response = await client.get(f"/api/v1/report/{run_id}?format=html")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert f"ehsa_report_{run_id[:8]}.html" in response.headers["content-disposition"]
        assert "<html>" in response.text
        assert run_id in response.text

    @pytest.mark.asyncio
    async def test_report_not_found(self, client):
        response = await client.get("/api/v1/report/invalid-id")
        assert response.status_code == 404
