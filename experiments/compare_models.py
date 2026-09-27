import os
import csv
import sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import settings
from app.preprocessing.preprocess import tokenize_code, parse_ast
from app.similarity.lexical import lexical_similarity
from app.similarity.structural import structural_similarity
from app.similarity.semantic import semantic_similarity, _model_cache, _model_lock
from app.similarity.behavioral import behavioral_similarity

THRESHOLD = 0.8

def load_dataset(dataset_dir):
    labels_csv = dataset_dir / "labels.csv"
    pairs = []
    with open(labels_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["pair_id"]
            label_str = row["label"]
            if label_str in ["1", "exact_copy", "variable_renaming", "structural_refactoring", "likely_ai_rewrite"]:
                label = 1
            else:
                label = 0
            pairs.append({
                "pair_id": pid,
                "file_a": f"{pid}_a.py",
                "file_b": f"{pid}_b.py",
                "label": label,
                "dataset_dir": dataset_dir
            })
    return pairs

def evaluate_with_model(model_name, all_pairs):
    print(f"\n--- Evaluating with Semantic Model: {model_name} ---")
    settings.MODEL_NAME = model_name
    
    # Clear model cache to force loading new model
    with _model_lock:
        _model_cache.clear()

    X = []
    y = []

    for p in all_pairs:
        file_a_path = p["dataset_dir"] / p["file_a"]
        file_b_path = p["dataset_dir"] / p["file_b"]
        
        code_a = file_a_path.read_text()
        code_b = file_b_path.read_text()

        tokens_a = tokenize_code(code_a)
        tokens_b = tokenize_code(code_b)
        ast_a = parse_ast(code_a)
        ast_b = parse_ast(code_b)

        lex, _ = lexical_similarity(tokens_a, tokens_b)
        struc, _ = structural_similarity(ast_a, ast_b)
        sem, _ = semantic_similarity(code_a, code_b)
        beh, _ = behavioral_similarity(code_a, code_b, [])

        lex = lex if lex is not None else 0.0
        struc = struc if struc is not None else 0.0
        sem = sem if sem is not None else 0.0
        beh = beh if beh is not None else 0.0
        
        X.append([lex, struc, sem, beh])
        y.append(p["label"])
        
    X = np.array(X)
    y = np.array(y)

    # Train Logistic Regression
    clf = LogisticRegression(penalty="l2", C=1.0, random_state=42)
    clf.fit(X, y)
    
    adaptive_prob_scores = clf.predict_proba(X)[:, 1]
    fixed_weights = np.array([0.20, 0.25, 0.35, 0.20])
    fixed_scores = np.dot(X, fixed_weights)

    results = {}
    for name, scores in [
        ("Semantic Alone", X[:, 2]),
        ("Fixed Fusion", fixed_scores),
        ("Adaptive Fusion", adaptive_prob_scores)
    ]:
        t = 0.5 if name == "Adaptive Fusion" else THRESHOLD
        preds = (scores >= t).astype(int)
        prec = precision_score(y, preds, zero_division=0)
        rec = recall_score(y, preds, zero_division=0)
        f1 = f1_score(y, preds, zero_division=0)
        try:
            auc = roc_auc_score(y, scores)
        except ValueError:
            auc = 0.5
        results[name] = {"precision": prec, "recall": rec, "f1": f1, "auc": auc}
        
    return results

def main():
    root_dir = Path(__file__).parent
    ds1_dir = root_dir / "dataset"
    ds2_dir = root_dir / "dataset" / "ojclone"
    
    pairs1 = load_dataset(ds1_dir)
    pairs2 = load_dataset(ds2_dir)
    all_pairs = pairs1 + pairs2
    
    unixcoder_res = evaluate_with_model("microsoft/unixcoder-base", all_pairs)
    graphcodebert_res = evaluate_with_model("microsoft/graphcodebert-base", all_pairs)

    print("\n" + "="*80)
    print("MODEL COMPARISON: UniXcoder vs GraphCodeBERT")
    print("="*80)
    print(f"{'Model / Metric':<35} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'AUC-ROC':<10}")
    print("-" * 80)
    
    for mname, res in [("microsoft/unixcoder-base", unixcoder_res), ("microsoft/graphcodebert-base", graphcodebert_res)]:
        print(f"Model: {mname}")
        for strategy, metrics in res.items():
            print(f"  {strategy:<33} | {metrics['precision']:<10.3f} | {metrics['recall']:<10.3f} | {metrics['f1']:<10.3f} | {metrics['auc']:<10.3f}")

if __name__ == "__main__":
    main()
