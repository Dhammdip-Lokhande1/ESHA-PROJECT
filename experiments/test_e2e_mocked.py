import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from httpx import ASGITransport, AsyncClient
from app.db.session import create_tables
from app.main import app

def _mock_semantic(code_a, code_b):
    return 0.82, [
        {
            "type": "cosine_similarity",
            "value": 0.82,
            "model": "microsoft/unixcoder-base",
            "token_count_a": 40,
            "token_count_b": 45,
            "note": "Mock semantic similarity for e2e test.",
        },
        {
            "type": "truncation_disclosure",
            "file": "both",
            "note": "No truncation applied.",
        },
    ]

async def main():
    print("--- Running Fast Live End-to-End API Verification ---")
    await create_tables()  # Ensure tables exist in SQLite
    
    code_a = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

    code_b = """
def fact(number):
    # Calculates factorial recursively
    if number <= 1:
        return 1
    return number * fact(number - 1)
"""

    import app.api.routes as routes_module
    with patch.object(routes_module, "semantic_similarity", _mock_semantic):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. POST /analyze
            resp = await client.post("/api/v1/analyze", json={
                "submission_code": code_a,
                "reference_code": code_b,
                "file_a_name": "submission.py",
                "file_b_name": "reference.py"
            })
            
            assert resp.status_code == 200, f"Error: {resp.status_code} - {resp.text}"
            data = resp.json()
            
            print("\n1. Analyze API Response Summary:")
            print(f"   Run ID: {data['run_id']}")
            print(f"   Fusion Score: {data['fusion_score']}")
            print(f"   Transformation Type: {data['explanation']['transformation_type']}")
            print(f"   Confidence Indicators: {data['confidence_indicators']}")
            print(f"   AI Generation Likelihood: {data['ai_generation']['likelihood']}")
            
            # 2. GET /report/{run_id}?format=json
            run_id = data['run_id']
            report_resp = await client.get(f"/api/v1/report/{run_id}?format=json")
            assert report_resp.status_code == 200
            report_data = report_resp.json()
            
            dimensions_in_db = set(e["dimension"] for e in report_data["evidence"])
            print("\n2. Evidence Dimensions Persisted to Database:")
            print(f"   Persisted Dimensions: {sorted(list(dimensions_in_db))}")
            
            assert "ai_generation" in dimensions_in_db, "ai_generation dimension missing from DB evidence!"
            assert "confidence_indicators" in data and data["confidence_indicators"] is not None
            
            # 3. GET /report/{run_id}?format=html
            html_resp = await client.get(f"/api/v1/report/{run_id}?format=html")
            assert html_resp.status_code == 200
            print("\n3. HTML Report Generation: SUCCESS")
            
            # 4. GET /report/{run_id}?format=pdf
            pdf_resp = await client.get(f"/api/v1/report/{run_id}?format=pdf")
            assert pdf_resp.status_code == 200
            print(f"\n4. PDF Report Endpoint: SUCCESS (Content-Type: {pdf_resp.headers['content-type']})")
            
    print("\n=========================================================")
    print("ALL LIVE END-TO-END VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(main())
