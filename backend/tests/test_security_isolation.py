"""
tests/test_security_isolation.py — Comprehensive security, IDOR, guest isolation, and rate-limiting test suite.
"""
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.rate_limiter import limiter
from app.db.models import Base, User
from app.db.session import get_db_dependency
from app.main import app


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
    limiter.reset()  # Reset rate limit state between tests
    yield session_factory
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def _mock_semantic():
    import app.api.routes as routes_module
    def fake_semantic(code_a, code_b):
        return 0.75, [{"type": "cosine_similarity", "value": 0.75}]
    return patch.object(routes_module, "semantic_similarity", fake_semantic)


@pytest.mark.asyncio
async def test_guest_analysis_and_privacy_isolation(client):
    """
    Verify that a guest can run an analysis, view their report by run_id,
    but guest runs do NOT leak into registered users' history list (/runs).
    """
    with _mock_semantic():
        # 1. Guest performs analysis (no auth header)
        resp = await client.post(
            "/api/v1/analyze",
            json={
                "submission_code": "def guest_func(): return 42",
                "reference_code": "def guest_func(): return 42",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        guest_run_id = data["run_id"]
        assert guest_run_id is not None

        # 2. Guest can fetch their own report via run_id
        report_resp = await client.get(f"/api/v1/report/{guest_run_id}")
        assert report_resp.status_code == 200

        # 3. Register a student user
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "clean_student", "email": "student@ehsa.edu", "password": "Password123!"},
        )
        assert reg_resp.status_code == 201

        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "clean_student", "password": "Password123!"},
        )
        token = login_resp.json()["access_token"]

        # 4. Student queries their history /runs -> MUST NOT contain the guest run!
        history_resp = await client.get(
            "/api/v1/runs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert history_resp.status_code == 200
        user_runs = history_resp.json()["runs"]
        user_run_ids = [r["id"] for r in user_runs]
        assert guest_run_id not in user_run_ids


@pytest.mark.asyncio
async def test_guest_run_claiming(client):
    """
    Verify that a guest who subsequently registers/logs in can claim their guest run
    and link it to their user account.
    """
    with _mock_semantic():
        # 1. Guest creates run
        guest_resp = await client.post(
            "/api/v1/analyze",
            json={"submission_code": "x = 100", "reference_code": "x = 100"},
        )
        guest_run_id = guest_resp.json()["run_id"]

        # 2. User registers & logs in
        await client.post(
            "/api/v1/auth/register",
            json={"username": "claimer_user", "email": "claim@ehsa.edu", "password": "Password123!"},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "claimer_user", "password": "Password123!"},
        )
        token = login_resp.json()["access_token"]

        # 3. User claims the guest run -> 200
        claim_resp = await client.post(
            f"/api/v1/runs/{guest_run_id}/claim",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert claim_resp.status_code == 200, claim_resp.text
        assert claim_resp.json()["status"] == "ok"

        # 4. Now the run appears in user's /runs history!
        history_resp = await client.get(
            "/api/v1/runs",
            headers={"Authorization": f"Bearer {token}"},
        )
        runs = history_resp.json()["runs"]
        assert any(r["id"] == guest_run_id for r in runs)


@pytest.mark.asyncio
async def test_unauthenticated_protected_endpoints_blocked(client):
    """
    Verify that unauthenticated guests cannot call feedback, dashboard, retrain, or history list.
    """
    # /runs without auth -> 401
    r1 = await client.get("/api/v1/runs")
    assert r1.status_code == 401

    # /feedback without auth -> 401
    r2 = await client.post("/api/v1/feedback/fake_id", json={"verdict": "confirmed"})
    assert r2.status_code == 401

    # /dashboard/my without auth -> 401
    r3_my = await client.get("/api/v1/dashboard/my")
    assert r3_my.status_code == 401

    # /instructor/dashboard without auth -> 401
    r3_inst = await client.get("/api/v1/instructor/dashboard")
    assert r3_inst.status_code == 401

    # /fusion/retrain without auth -> 401
    r4 = await client.post("/api/v1/fusion/retrain")
    assert r4.status_code == 401


@pytest.mark.asyncio
async def test_rate_limiting_enforcement(client):
    """
    Verify that exceeding the rate limit on /auth/login returns HTTP 429.
    """
    limiter.reset()
    # Rate limit on login is 15 requests/min.
    responses = []
    for _ in range(16):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "rate_test", "password": "wrong_password"},
        )
        responses.append(resp.status_code)

    # At least the 16th request must receive HTTP 429
    assert 429 in responses
