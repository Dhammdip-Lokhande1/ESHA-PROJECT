import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from httpx import ASGITransport, AsyncClient
from app.db.session import create_tables, get_db
from app.main import app
from sqlalchemy import select
from app.db.models import Run

def _mock_semantic(code_a, code_b):
    return 0.75, [{"type": "cosine_similarity", "value": 0.75, "model": "mock-model"}]

async def main():
    print("--- Fast Verification for Retrained Adaptive Weights ---")
    await create_tables()

    code_a = "def multiply(x, y):\n    return x * y\n"
    code_b = "def mult(a, b):\n    return a * b\n"

    import app.api.routes as routes_module
    with patch.object(routes_module, "semantic_similarity", _mock_semantic):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Check GET /fusion/weights
            w_resp = await client.get("/api/v1/fusion/weights")
            assert w_resp.status_code == 200
            w_data = w_resp.json()
            print("\n1. Current Fusion Weights Endpoint:")
            print(f"   Source: {w_data.get('source')}")
            print(f"   Last Updated: {w_data.get('last_updated')}")
            print(f"   Current Weights: {w_data.get('current_weights')}")

            assert w_data.get("source") == "adaptive_trained", f"Expected 'adaptive_trained', got '{w_data.get('source')}'"

            # 2. POST /analyze
            resp = await client.post("/api/v1/analyze", json={
                "submission_code": code_a,
                "reference_code": code_b,
                "file_a_name": "mult_a.py",
                "file_b_name": "mult_b.py"
            })
            assert resp.status_code == 200
            data = resp.json()

            print("\n2. Live API /analyze Response:")
            print(f"   Run ID: {data['run_id']}")
            print(f"   Fusion Score: {data['fusion_score']}")
            print(f"   Weight Metadata Source: {data['fusion_weight_metadata']['source']}")
            print(f"   Effective Weights: {data['fusion_weight_metadata']['effective_weights']}")

            assert data['fusion_weight_metadata']['source'] == "adaptive_trained"

            # 3. Query Run row from DB
            async with get_db() as db:
                run_row = (await db.execute(select(Run).where(Run.id == data['run_id']))).scalar_one_or_none()
                assert run_row is not None
                print("\n3. DB Persisted Run Record:")
                print(f"   DB Run ID: {run_row.id}")
                print(f"   DB Fusion Score: {run_row.fusion_score}")
                print(f"   DB Weights Used: {run_row.fusion_weights_used}")

    print("\n=========================================================")
    print("VERIFICATION SUCCESS: RETRAINED ADAPTIVE WEIGHTS ACTIVE!")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(main())
