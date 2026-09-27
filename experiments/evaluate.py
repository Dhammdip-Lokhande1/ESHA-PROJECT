import asyncio
import csv
import sys
from pathlib import Path
import httpx
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

DATASET_DIR = Path(__file__).parent / "dataset" / "ojclone"
LABELS_CSV = DATASET_DIR / "labels.csv"
THRESHOLD = 0.8

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.main import app


def load_labels():
    pairs = []
    with open(LABELS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["pair_id"]
            label = 1 if row["label"] in ["exact_copy", "structural_refactoring"] else 0
            pairs.append({
                "pair_id": pid,
                "file_a": f"{pid}_a.py",
                "file_b": f"{pid}_b.py",
                "label": label
            })
    return pairs


async def run_evaluation():
    pairs = load_labels()
    print(f"Evaluating {len(pairs)} pairs from OJClone benchmark...")
    
    # Ensure DB tables and column migrations are applied
    from app.db.session import create_tables
    await create_tables()

    X = []
    y = []

    # Check if a live server is running first
    live_client = None
    try:
        c = httpx.Client(timeout=2.0)
        r = c.get("http://127.0.0.1:8000/health")
        if r.status_code == 200:
            live_client = c
    except Exception:
        pass

    if live_client:
        client = live_client
        url = "http://127.0.0.1:8000/api/v1/analyze"
        for p in pairs:
            code_a = (DATASET_DIR / p["file_a"]).read_text()
            code_b = (DATASET_DIR / p["file_b"]).read_text()
            resp = client.post(url, json={"submission_code": code_a, "reference_code": code_b})
            resp.raise_for_status()
            data = resp.json()
            c = data["components"]
            lex = c.get("lexical", 0.0)
            struc = c.get("structural", 0.0)
            sem = c.get("semantic", 0.0)
            beh = float(c.get("behavioral") or 0.0)
            X.append([lex, struc, sem, beh])
            y.append(p["label"])
    else:
        # Use ASGI transport with AsyncClient standalone
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
            for p in pairs:
                code_a = (DATASET_DIR / p["file_a"]).read_text()
                code_b = (DATASET_DIR / p["file_b"]).read_text()
                resp = await client.post("/api/v1/analyze", json={"submission_code": code_a, "reference_code": code_b})
                resp.raise_for_status()
                data = resp.json()
                c = data["components"]
                lex = c.get("lexical", 0.0)
                struc = c.get("structural", 0.0)
                sem = c.get("semantic", 0.0)
                beh = float(c.get("behavioral") or 0.0)
                X.append([lex, struc, sem, beh])
                y.append(p["label"])

    X = np.array(X)
    y = np.array(y)

    # Train Adaptive Fusion (Logistic Regression)
    clf = LogisticRegression(fit_intercept=False, penalty="l2", C=1.0)
    if len(np.unique(y)) > 1:
        clf.fit(X, y)
        coefs = np.clip(clf.coef_[0], a_min=0.01, a_max=None)
        adaptive_weights = coefs / np.sum(coefs)
    else:
        adaptive_weights = [0.25, 0.25, 0.25, 0.25]

    print(f"\nLearned Adaptive Weights: Lex={adaptive_weights[0]:.2f}, Struct={adaptive_weights[1]:.2f}, Sem={adaptive_weights[2]:.2f}, Beh={adaptive_weights[3]:.2f}\n")

    strategies = {
        "Lexical": X[:, 0],
        "Structural": X[:, 1],
        "Semantic": X[:, 2],
        "Behavioral": X[:, 3],
        "Fixed Fusion": np.mean(X, axis=1),
        "Adaptive Fusion": np.dot(X, adaptive_weights)
    }

    print("# Baseline Benchmark Results\n")
    print("| Component / Strategy | Precision | Recall | F1-Score | AUC-ROC |")
    print("|----------------------|-----------|--------|----------|---------|")

    md_rows = []
    for name, scores in strategies.items():
        t = 0.5 if name == "Adaptive Fusion" else THRESHOLD
        preds = (scores >= t).astype(int)

        if np.sum(preds) == 0 and np.sum(y) == 0:
            prec, rec, f1 = 1.0, 1.0, 1.0
        else:
            prec = precision_score(y, preds, zero_division=0)
            rec = recall_score(y, preds, zero_division=0)
            f1 = f1_score(y, preds, zero_division=0)

        try:
            auc = roc_auc_score(y, scores)
        except ValueError:
            auc = 0.5

        row_str = f"| {name} | {prec:.3f} | {rec:.3f} | {f1:.3f} | {auc:.3f} |"
        print(row_str)
        md_rows.append(row_str)

    out_md = Path(__file__).parent.parent / "ablation_results.md"
    with open(out_md, "w") as f:
        f.write("# Ablation & Benchmark Results\n\n")
        f.write("| Component / Strategy | Precision | Recall | F1-Score | AUC-ROC |\n")
        f.write("|----------------------|-----------|--------|----------|---------|\n")
        for r in md_rows:
            f.write(r + "\n")


def main():
    asyncio.run(run_evaluation())


if __name__ == "__main__":
    main()
