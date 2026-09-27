"""
experiments/e2e_live_scenarios.py
==================================
End-to-end live scenario verification covering all 7 scenarios a-g.
Run with:  python experiments/e2e_live_scenarios.py
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from httpx import ASGITransport, AsyncClient
from app.db.session import create_tables, get_db
from app.db.models import FusionWeightHistory, Run, Evidence, Feedback
from app.main import app
from sqlalchemy import select

results = {}

def _mock_semantic(code_a, code_b):
    tok_a = set(code_a.split())
    tok_b = set(code_b.split())
    sim = len(tok_a & tok_b) / max(len(tok_a | tok_b), 1)
    return float(sim), [
        {"type": "cosine_similarity", "value": float(sim), "model": "mock-unixcoder",
         "token_count_a": len(tok_a), "token_count_b": len(tok_b),
         "note": "Mocked semantic score for live scenario test."},
        {"type": "truncation_disclosure", "file": "both", "note": "No truncation applied."}
    ]


IDENTICAL_CODE = """\
def add(a, b):
    result = a + b
    return result

def multiply(x, y):
    return x * y
"""

RENAMED_CODE = """\
def total(first, second):
    value = first + second
    return value

def product(p, q):
    return p * q
"""

UNRELATED_CODE = """\
import os
import sys

def parse_args():
    args = sys.argv[1:]
    return args

def list_files(directory):
    return os.listdir(directory)
"""


async def run_scenarios():
    await create_tables()

    import app.api.routes as routes_module
    with patch.object(routes_module, "semantic_similarity", _mock_semantic):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

            # Scenario a: Identical files
            print("\n--- Scenario a: Identical files ---")
            r = await client.post("/api/v1/analyze", json={
                "submission_code": IDENTICAL_CODE,
                "reference_code": IDENTICAL_CODE,
                "file_a_name": "identical_a.py",
                "file_b_name": "identical_b.py",
            })
            d = r.json()
            sa_fusion = d["fusion_score"]
            sa_lex = d["components"]["lexical"]
            sa_struct = d["components"]["structural"]
            sa_ttype = d["explanation"]["transformation_type"]
            sa_conf = d["confidence_indicators"]
            ev_populated = all(len(d["components"][f"{k}_evidence"]) > 0
                               for k in ["lexical", "structural", "semantic", "behavioral"])

            ok = (sa_fusion >= 0.85 and sa_lex >= 0.99 and sa_struct >= 0.99
                  and sa_ttype == "exact_copy" and sa_conf is not None and ev_populated)
            results["a"] = "PASS" if ok else "FAIL"
            print(f"  fusion={sa_fusion:.3f}, lex={sa_lex:.3f}, struct={sa_struct:.3f}, type={sa_ttype}")
            print(f"  confidence_indicators={sa_conf}")
            print(f"  evidence populated: {ev_populated}")
            print(f"  -> {results['a']}")

            # Scenario b: Variable-renamed pair
            print("\n--- Scenario b: Variable-renamed pair ---")
            r = await client.post("/api/v1/analyze", json={
                "submission_code": IDENTICAL_CODE,
                "reference_code": RENAMED_CODE,
                "file_a_name": "original.py",
                "file_b_name": "renamed.py",
            })
            d = r.json()
            sb_lex = d["components"]["lexical"]
            sb_struct = d["components"]["structural"]
            sb_ttype = d["explanation"]["transformation_type"]
            sb_verdict = d["explanation"]["verdict"]
            sb_narrative = d["explanation"]["narrative"]
            # verdict references fusion score; narrative references struct + lex directly (spec 9.2)
            score_referenced = (str(round(sb_struct, 2)) in sb_verdict
                                or str(round(sb_lex, 2)) in sb_verdict
                                or str(round(sb_struct, 2)) in sb_narrative
                                or str(round(sb_lex, 2)) in sb_narrative
                                or "structural" in sb_verdict.lower()
                                or "lexical" in sb_verdict.lower()
                                or "structural" in sb_narrative.lower())
            ok = sb_lex < 0.7 and sb_struct >= 0.7 and sb_ttype == "variable_renaming" and score_referenced
            results["b"] = "PASS" if ok else "FAIL"
            print(f"  lex={sb_lex:.3f}, struct={sb_struct:.3f}, type={sb_ttype}")
            print(f"  verdict (first 140 chars): {sb_verdict[:140]}...")
            print(f"  score_referenced_in_verdict={score_referenced}")
            print(f"  -> {results['b']}")

            # Scenario c: Genuinely unrelated pair
            print("\n--- Scenario c: Unrelated pair (regression test for Rule-5 bug) ---")
            r = await client.post("/api/v1/analyze", json={
                "submission_code": UNRELATED_CODE,
                "reference_code": RENAMED_CODE,
                "file_a_name": "unrelated.py",
                "file_b_name": "renamed.py",
            })
            d = r.json()
            sc_fusion = d["fusion_score"]
            sc_ttype = d["explanation"]["transformation_type"]
            ok = sc_ttype == "unrelated" and sc_fusion < 0.35
            results["c"] = "PASS" if ok else "FAIL"
            print(f"  fusion={sc_fusion:.3f}, type={sc_ttype}")
            print(f"  -> {results['c']}")

            # Scenario d: Instructor feedback (both verdicts)
            print("\n--- Scenario d: Feedback submission & DB storage ---")
            r = await client.post("/api/v1/analyze", json={
                "submission_code": IDENTICAL_CODE,
                "reference_code": RENAMED_CODE,
            })
            run_id = r.json()["run_id"]
            confirm_r = await client.post(f"/api/v1/feedback/{run_id}", json={"verdict": "confirmed"})

            r2 = await client.post("/api/v1/analyze", json={
                "submission_code": UNRELATED_CODE,
                "reference_code": RENAMED_CODE,
            })
            run_id2 = r2.json()["run_id"]
            fp_r = await client.post(f"/api/v1/feedback/{run_id2}", json={"verdict": "false_positive"})

            async with get_db() as db:
                fb1 = (await db.execute(select(Feedback).where(Feedback.run_id == run_id))).scalar_one_or_none()
                fb2 = (await db.execute(select(Feedback).where(Feedback.run_id == run_id2))).scalar_one_or_none()

            ok = (confirm_r.status_code == 200 and fp_r.status_code == 200
                  and fb1 is not None and fb1.verdict == "confirmed"
                  and fb2 is not None and fb2.verdict == "false_positive")
            results["d"] = "PASS" if ok else "FAIL"
            print(f"  confirmed verdict in DB: {fb1.verdict if fb1 else 'MISSING'}")
            print(f"  false_positive verdict in DB: {fb2.verdict if fb2 else 'MISSING'}")
            print(f"  -> {results['d']}")

            # Scenario e: Dashboard endpoint
            print("\n--- Scenario e: Dashboard summary ---")
            dash_r = await client.get("/api/v1/dashboard/summary")
            dash_d = dash_r.json()
            ok = (dash_r.status_code == 200
                  and dash_d.get("total_runs", 0) > 0
                  and "score_distribution" in dash_d
                  and "transformation_breakdown" in dash_d
                  and "weight_drift_history" in dash_d
                  and "calibration_data" in dash_d)
            results["e"] = "PASS" if ok else "FAIL"
            print(f"  total_runs={dash_d.get('total_runs')}, avg_fusion={dash_d.get('avg_fusion_score')}")
            print(f"  score_distribution len={len(dash_d.get('score_distribution', []))}")
            print(f"  transformation_breakdown={dash_d.get('transformation_breakdown')}")
            print(f"  weight_drift_history len={len(dash_d.get('weight_drift_history', []))}")
            print(f"  -> {results['e']}")

            # Scenario f: Batch comparison
            print("\n--- Scenario f: Batch comparison matrix ---")
            batch_r = await client.post(
                "/api/v1/compare/batch",
                files=[
                    ("files", ("a.py", IDENTICAL_CODE.encode())),
                    ("files", ("b.py", RENAMED_CODE.encode())),
                    ("files", ("c.py", UNRELATED_CODE.encode())),
                ],
            )
            batch_d = batch_r.json()
            ok = (batch_r.status_code == 200
                  and "matrix" in batch_d
                  and len(batch_d["matrix"]) == 3
                  and all("fusion_score" in row and "transformation_type" in row
                          for row in batch_d["matrix"]))
            results["f"] = "PASS" if ok else "FAIL"
            print(f"  matrix pairs: {len(batch_d.get('matrix', []))}")
            for row in batch_d.get("matrix", []):
                print(f"    {row['file_a']} vs {row['file_b']}: fusion={row['fusion_score']:.3f}, type={row['transformation_type']}")
            print(f"  -> {results['f']}")

            # Scenario g: Fusion weights endpoint
            print("\n--- Scenario g: FusionWeightsPanel ---")
            w_r = await client.get("/api/v1/fusion/weights")
            w_d = w_r.json()
            ok = (w_r.status_code == 200
                  and w_d.get("source") == "adaptive_trained"
                  and w_d.get("last_updated") is not None
                  and all(k in w_d.get("current_weights", {})
                          for k in ["lexical", "structural", "semantic", "behavioral"]))
            results["g"] = "PASS" if ok else "FAIL"
            print(f"  source={w_d.get('source')}")
            print(f"  last_updated={w_d.get('last_updated')}")
            print(f"  current_weights={w_d.get('current_weights')}")
            print(f"  -> {results['g']}")

    return results


async def main():
    print("=" * 70)
    print("EHSA END-TO-END LIVE SCENARIO VERIFICATION")
    print("=" * 70)
    res = await run_scenarios()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for k, v in sorted(res.items()):
        print(f"  Scenario {k}: {v}")
    passed = sum(1 for v in res.values() if v == "PASS")
    total = len(res)
    print(f"\n  {passed}/{total} scenarios passed")
    if passed < total:
        print("  WARNING: Some scenarios failed -- see above for details")
    else:
        print("  All scenarios passed!")


if __name__ == "__main__":
    asyncio.run(main())
