"""
experiments/evaluate_adaptive_learning_curve.py
================================================
Phase 6: Adaptive Learning Curve Evaluation

Evaluates how the adaptive fusion engine adapts as instructor feedback pairs (k)
are provided: k in {0, 5, 10, 20, 50, 100}.
Compares 0% label noise vs 10% label noise over 20 random seeds.
Saves metrics, markdown table, and learning curve plot.
"""
from __future__ import annotations

import json
import os
import sys
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.fusion.fusion_engine import fuse
from app.config import settings

OUT_DIR = ROOT_DIR / "experiments" / "results" / "adaptive_learning_curve"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TRANSBENCH_PATH = ROOT_DIR / "experiments" / "dataset" / "transbench_lite" / "pairs.csv"
PAIR_CACHE_FILE = ROOT_DIR / "experiments" / "cache" / "pair_cache.pkl"

def load_code(rel_path: str) -> str:
    full_path = ROOT_DIR / "experiments" / "dataset" / "transbench_lite" / rel_path
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def compute_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    if tp + fp == 0 or tp + fn == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall == 0:
        return 0.0
    return float(2 * precision * recall / (precision + recall))

def train_adaptive_weights(X_k: np.ndarray, y_k: np.ndarray) -> dict[str, float]:
    """
    Train weights using LogisticRegression matching app.fusion.adaptive_trainer.retrain_fusion_weights.
    """
    if len(X_k) < 2 or len(np.unique(y_k)) < 2:
        return settings.FUSION_WEIGHTS.copy()
    
    clf = LogisticRegression(fit_intercept=False, penalty="l2", C=1.0)
    try:
        clf.fit(X_k, y_k)
        coefs = clf.coef_[0]
        coefs = np.clip(coefs, a_min=0.01, a_max=None)
        weights_normalized = coefs / np.sum(coefs)
        return {
            "lexical": float(weights_normalized[0]),
            "structural": float(weights_normalized[1]),
            "semantic": float(weights_normalized[2]),
            "behavioral": float(weights_normalized[3]),
        }
    except Exception:
        return settings.FUSION_WEIGHTS.copy()

def run_adaptive_experiment():
    print("[+] Loading TransBench-Lite dataset and cached features...")
    df_pairs = pd.read_csv(TRANSBENCH_PATH)
    
    pair_cache = {}
    if PAIR_CACHE_FILE.exists():
        with open(PAIR_CACHE_FILE, "rb") as f:
            pair_cache = pickle.load(f)
            
    # Extract feature matrix for all pairs
    feats = []
    for r in df_pairs.to_dict("records"):
        ca = load_code(r["code_a_path"])
        cb = load_code(r["code_b_path"])
        key = (ca, cb) if ca <= cb else (cb, ca)
        if key in pair_cache and isinstance(pair_cache[key], (tuple, list)) and len(pair_cache[key]) == 5:
            l_val, s_val, m_val, b_val, _ = pair_cache[key]
        else:
            l_val, s_val, m_val, b_val = 0.5, 0.5, 0.5, 0.5
            
        b_imputed = b_val if b_val is not None else 0.5
        feats.append({
            "pair_id": r["pair_id"],
            "split": r["split"],
            "label": int(r["label"]),
            "lexical": l_val,
            "structural": s_val,
            "semantic": m_val,
            "behavioral": b_imputed,
        })
        
    df_feats = pd.DataFrame(feats)
    train_df = df_feats[df_feats["split"] == "train"].reset_index(drop=True)
    test_df = df_feats[df_feats["split"] == "test"].reset_index(drop=True)
    
    X_train = train_df[["lexical", "structural", "semantic", "behavioral"]].values
    y_train = train_df["label"].values.astype(int)
    
    X_test = test_df[["lexical", "structural", "semantic", "behavioral"]].values
    y_test = test_df["label"].values.astype(int)
    
    k_values = [0, 5, 10, 20, 50, 100]
    n_seeds = 20
    
    results = {
        "clean_0pct": {k: [] for k in k_values},
        "noisy_10pct": {k: [] for k in k_values}
    }
    
    print(f"[+] Running Adaptive Learning Curve Study ({n_seeds} seeds, k={k_values})...")
    
    for seed in range(n_seeds):
        rng = np.random.RandomState(seed + 42)
        
        # Permute train data for sampling
        perm = rng.permutation(len(train_df))
        X_train_perm = X_train[perm]
        y_train_perm = y_train[perm]
        
        # 10% label noise mask
        noise_mask = rng.rand(len(train_df)) < 0.10
        y_train_noisy = np.where(noise_mask, 1 - y_train_perm, y_train_perm)
        
        for k in k_values:
            # --- 1. Clean (0% noise) ---
            if k == 0:
                w_clean = settings.FUSION_WEIGHTS.copy()
            else:
                X_k = X_train_perm[:k]
                y_k = y_train_perm[:k]
                w_clean = train_adaptive_weights(X_k, y_k)
            
            # Predict on test set
            preds_clean = []
            for x_i in X_test:
                scores = {"lexical": float(x_i[0]), "structural": float(x_i[1]), "semantic": float(x_i[2]), "behavioral": float(x_i[3])}
                fused, _ = fuse(scores, weights=w_clean)
                preds_clean.append(1 if fused >= 0.5 else 0)
            f1_clean = compute_f1(y_test, np.array(preds_clean))
            results["clean_0pct"][k].append(f1_clean)
            
            # --- 2. Noisy (10% noise) ---
            if k == 0:
                w_noisy = settings.FUSION_WEIGHTS.copy()
            else:
                X_k = X_train_perm[:k]
                y_k_noisy = y_train_noisy[:k]
                w_noisy = train_adaptive_weights(X_k, y_k_noisy)
            
            preds_noisy = []
            for x_i in X_test:
                scores = {"lexical": float(x_i[0]), "structural": float(x_i[1]), "semantic": float(x_i[2]), "behavioral": float(x_i[3])}
                fused, _ = fuse(scores, weights=w_noisy)
                preds_noisy.append(1 if fused >= 0.5 else 0)
            f1_noisy = compute_f1(y_test, np.array(preds_noisy))
            results["noisy_10pct"][k].append(f1_noisy)

    # Compute summary statistics (Mean and 95% CIs)
    summary_data = []
    plot_stats = {"clean": {"k": [], "mean": [], "ci_low": [], "ci_high": []},
                  "noisy": {"k": [], "mean": [], "ci_low": [], "ci_high": []}}
    
    for k in k_values:
        clean_scores = np.array(results["clean_0pct"][k])
        noisy_scores = np.array(results["noisy_10pct"][k])
        
        c_mean, c_std = np.mean(clean_scores), np.std(clean_scores, ddof=1)
        c_ci = 1.96 * (c_std / np.sqrt(n_seeds)) if n_seeds > 1 else 0.0
        
        n_mean, n_std = np.mean(noisy_scores), np.std(noisy_scores, ddof=1)
        n_ci = 1.96 * (n_std / np.sqrt(n_seeds)) if n_seeds > 1 else 0.0
        
        plot_stats["clean"]["k"].append(k)
        plot_stats["clean"]["mean"].append(c_mean)
        plot_stats["clean"]["ci_low"].append(c_mean - c_ci)
        plot_stats["clean"]["ci_high"].append(c_mean + c_ci)
        
        plot_stats["noisy"]["k"].append(k)
        plot_stats["noisy"]["mean"].append(n_mean)
        plot_stats["noisy"]["ci_low"].append(n_mean - n_ci)
        plot_stats["noisy"]["ci_high"].append(n_mean + n_ci)
        
        summary_data.append({
            "k": k,
            "clean_f1_mean": round(float(c_mean), 4),
            "clean_f1_ci95": f"±{round(float(c_ci), 4)}",
            "noisy_f1_mean": round(float(n_mean), 4),
            "noisy_f1_ci95": f"±{round(float(n_ci), 4)}"
        })

    # Save JSON metrics
    metrics_path = OUT_DIR / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "n_seeds": n_seeds,
            "k_values": k_values,
            "summary": summary_data,
            "raw_results": results
        }, f, indent=2)
    print(f"[OK] Saved metrics to {metrics_path}")

    # Generate Markdown Table
    md_table_path = OUT_DIR / "learning_curve_table.md"
    md_content = "# Phase 6: Adaptive Fusion Learning Curve Evaluation\n\n"
    md_content += f"Evaluated across N={n_seeds} random seeds on TransBench-Lite test split (120 pairs).\n\n"
    md_content += "| Feedback Samples ($k$) | Clean Feedback F1 (0% noise) | Noisy Feedback F1 (10% noise) |\n"
    md_content += "|-------------------------|--------------------------------|--------------------------------|\n"
    for row in summary_data:
        md_content += f"| k = {row['k']} | {row['clean_f1_mean']:.4f} {row['clean_f1_ci95']} | {row['noisy_f1_mean']:.4f} {row['noisy_f1_ci95']} |\n"
    
    with open(md_table_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Saved markdown table to {md_table_path}")

    # Plot Learning Curve
    plt.figure(figsize=(8, 5))
    plt.plot(plot_stats["clean"]["k"], plot_stats["clean"]["mean"], 'o-', color='#1e88e5', linewidth=2.5, label='Clean Feedback (0% Noise)')
    plt.fill_between(plot_stats["clean"]["k"], plot_stats["clean"]["ci_low"], plot_stats["clean"]["ci_high"], color='#1e88e5', alpha=0.2)
    
    plt.plot(plot_stats["noisy"]["k"], plot_stats["noisy"]["mean"], 's--', color='#e53935', linewidth=2.5, label='Noisy Feedback (10% Noise)')
    plt.fill_between(plot_stats["noisy"]["k"], plot_stats["noisy"]["ci_low"], plot_stats["noisy"]["ci_high"], color='#e53935', alpha=0.2)
    
    plt.title("EHSA Adaptive Fusion Engine Learning Curve", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Number of Feedback Pair Updates ($k$)", fontsize=11, labelpad=8)
    plt.ylabel("Test Set F1 Score", fontsize=11, labelpad=8)
    plt.xticks(k_values)
    plt.ylim(0.80, 1.01)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(frameon=True, loc='lower right', fontsize=10)
    plt.tight_layout()
    
    plot_path = OUT_DIR / "learning_curve.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[OK] Saved learning curve plot to {plot_path}")

if __name__ == "__main__":
    run_adaptive_experiment()
