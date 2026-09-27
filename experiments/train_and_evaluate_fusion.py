import os
import csv
import sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.preprocessing.preprocess import tokenize_code, parse_ast
from app.similarity.lexical import lexical_similarity
from app.similarity.structural import structural_similarity
from app.similarity.semantic import semantic_similarity
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

def main():
    root_dir = Path(__file__).parent
    ds1_dir = root_dir / "dataset"
    ds2_dir = root_dir / "dataset" / "ojclone"
    
    pairs1 = load_dataset(ds1_dir)
    pairs2 = load_dataset(ds2_dir)
    all_pairs = pairs1 + pairs2
    print(f"Loaded total {len(all_pairs)} pairs ({len(pairs1)} synthetic + {len(pairs2)} OJClone)...")

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
    
    print(f"Class distribution: {np.sum(y==1)} positive, {np.sum(y==0)} negative.")

    # Fixed weights
    fixed_weights = np.array([0.20, 0.25, 0.35, 0.20])
    fixed_scores = np.dot(X, fixed_weights)

    # Train Adaptive Fusion (Logistic Regression)
    # We fit Logistic Regression on X to predict y
    clf = LogisticRegression(penalty="l2", C=1.0, random_state=42)
    clf.fit(X, y)
    
    adaptive_prob_scores = clf.predict_proba(X)[:, 1]
    
    coefs = np.clip(clf.coef_[0], a_min=0.01, a_max=None)
    adaptive_weights = coefs / np.sum(coefs)
    print(f"Learned Linear Weights: Lex={adaptive_weights[0]:.4f}, Struct={adaptive_weights[1]:.4f}, Sem={adaptive_weights[2]:.4f}, Beh={adaptive_weights[3]:.4f}")
    adaptive_dot_scores = np.dot(X, adaptive_weights)

    strategies = {
        "Lexical": X[:, 0],
        "Structural": X[:, 1],
        "Semantic": X[:, 2],
        "Behavioral": X[:, 3],
        "Fixed Fusion": fixed_scores,
        "Adaptive Fusion (Linear)": adaptive_dot_scores,
        "Adaptive Fusion (Probability)": adaptive_prob_scores,
    }

    print("\n" + "="*75)
    print("COMPREHENSIVE FUSION ABLATION RESULTS")
    print("="*75)
    print(f"{'Component':<32} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'AUC-ROC':<10}")
    print("-" * 78)

    for name, scores in strategies.items():
        if "Probability" in name:
            t = 0.5
        else:
            t = THRESHOLD
            
        preds = (scores >= t).astype(int)
        
        prec = precision_score(y, preds, zero_division=0)
        rec = recall_score(y, preds, zero_division=0)
        f1 = f1_score(y, preds, zero_division=0)
        try:
            auc = roc_auc_score(y, scores)
        except ValueError:
            auc = 0.5
            
        print(f"{name:<32} | {prec:<10.3f} | {rec:<10.3f} | {f1:<10.3f} | {auc:<10.3f}")

if __name__ == "__main__":
    main()
