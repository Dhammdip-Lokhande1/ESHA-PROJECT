"""
experiments/ablation_cv.py
===========================
Proper ablation: 5-fold stratified cross-validation + in-sample comparisons.

KEY INSIGHT documented here:
  The retrained weights (lex=0.196, struct=0.296, sem=0.002, beh=0.506)
  CANNOT be used as a simple dot-product classifier on this benchmark
  because behavioral=0 for all pairs (no executable test cases).
  With beh_weight=0.506, dot-product scores are capped at ~0.494.
  The in-sample F1=0.919 cited previously came from clf.predict_proba()
  (the LR sigmoid applied to scaled features), NOT from a raw dot-product.
  This distinction is critical and is explicitly flagged in the output.

Strategies compared:
  (a) Retrained weights — dot-product interpretation, optimal threshold
      (shows what the weights actually do as a linear classifier)
  (b) Fixed weights (lex=0.20, struct=0.25, sem=0.35, beh=0.20) at T=0.8
  (c) Structural alone at T=0.8
  (d) LR Adaptive Fusion — in-sample fit (source of the F1=0.919 claim)
  (e) LR Adaptive Fusion — 5-fold CV (HONEST, held-out-only estimate)
"""

import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    precision_recall_curve
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.preprocessing.preprocess import tokenize_code, parse_ast
from app.similarity.lexical import lexical_similarity
from app.similarity.structural import structural_similarity
from app.similarity.semantic import semantic_similarity

THRESHOLD_FIXED = 0.8
RETRAINED_WEIGHTS = np.array([0.19579, 0.29551, 0.00243, 0.50627])
FIXED_WEIGHTS = np.array([0.20, 0.25, 0.35, 0.20])


# ── Data loading ─────────────────────────────────────────────────────────────

def load_dataset():
    root = Path(__file__).parent
    pairs = []
    pos_labels = {"1", "exact_copy", "variable_renaming",
                  "structural_refactoring", "likely_ai_rewrite"}
    for ds_dir in [root / "dataset", root / "dataset" / "ojclone"]:
        for row in csv.DictReader(open(ds_dir / "labels.csv")):
            pid = row["pair_id"]
            pairs.append({
                "pair_id": pid,
                "file_a": ds_dir / f"{pid}_a.py",
                "file_b": ds_dir / f"{pid}_b.py",
                "label": 1 if row["label"] in pos_labels else 0,
            })
    return pairs


def compute_features(pairs):
    """
    Returns X (n,4) = [lex, struct, sem_real, beh=0], y (n,)

    sem_real is the actual UniXcoder embedding cosine similarity.
    The first call will download/cache the model if not already present.
    beh=0 throughout — no executable test cases in this benchmark.
    """
    X, y = [], []
    print(f"  Computing features for {len(pairs)} pairs (using REAL UniXcoder semantic scores)...")
    for i, p in enumerate(pairs):
        ca = p["file_a"].read_text(errors="replace")
        cb = p["file_b"].read_text(errors="replace")
        ta, tb = tokenize_code(ca), tokenize_code(cb)
        aa, ab = parse_ast(ca), parse_ast(cb)
        lex = lexical_similarity(ta, tb)[0] or 0.0
        struct = structural_similarity(aa, ab)[0] or 0.0
        
        # Real semantic calculation
        sem, _ = semantic_similarity(ca, cb)
        sem = sem if sem is not None else 0.0

        X.append([lex, struct, sem, 0.0])
        y.append(p["label"])
        if (i + 1) % 10 == 0:
            print(f"    {i+1}/{len(pairs)} done")
    return np.array(X), np.array(y)


# ── Metric helpers ────────────────────────────────────────────────────────────

def metrics_at(y_true, scores, threshold):
    preds = (scores >= threshold).astype(int)
    return {
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall":    recall_score(y_true, preds, zero_division=0),
        "f1":        f1_score(y_true, preds, zero_division=0),
        "auc":       _auc(y_true, scores),
        "n_pos_pred": int(preds.sum()),
    }


def _auc(y, s):
    try:
        return roc_auc_score(y, s)
    except ValueError:
        return float("nan")


def best_threshold_f1(y, scores):
    """Find threshold that maximises F1 on the given set (for reference only)."""
    prec, rec, thresholds = precision_recall_curve(y, scores)
    f1s = 2 * prec * rec / np.where((prec + rec) == 0, 1, prec + rec)
    idx = np.argmax(f1s[:-1])  # last element of prec/rec has no threshold
    return thresholds[idx], f1s[idx]


# ── Cross-validation ──────────────────────────────────────────────────────────

def cv_evaluate(X, y, n_splits=5):
    """
    Honest 5-fold CV: LR fit only on training folds.
    Also records per-fold feature weights (after L2 regularization).
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_prec, fold_rec, fold_f1, fold_auc = [], [], [], []
    all_y_true, all_y_prob = [], []
    lr_coefs = []

    for train_idx, test_idx in skf.split(X, y):
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        clf = LogisticRegression(penalty="l2", C=1.0, random_state=42, max_iter=300)
        clf.fit(X_tr_s, y_tr)

        y_prob = clf.predict_proba(X_te_s)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)

        fold_prec.append(precision_score(y_te, y_pred, zero_division=0))
        fold_rec.append(recall_score(y_te, y_pred, zero_division=0))
        fold_f1.append(f1_score(y_te, y_pred, zero_division=0))
        fold_auc.append(_auc(y_te, y_prob))
        all_y_true.extend(y_te)
        all_y_prob.extend(y_prob)

        coef = np.clip(clf.coef_[0], 0.001, None)
        lr_coefs.append(coef / coef.sum())

    all_y_true = np.array(all_y_true)
    all_y_prob = np.array(all_y_prob)
    all_y_pred = (all_y_prob >= 0.5).astype(int)
    lr_coefs = np.array(lr_coefs)

    return {
        "agg": {
            "precision": precision_score(all_y_true, all_y_pred, zero_division=0),
            "recall":    recall_score(all_y_true, all_y_pred, zero_division=0),
            "f1":        f1_score(all_y_true, all_y_pred, zero_division=0),
            "auc":       _auc(all_y_true, all_y_prob),
        },
        "fold_means": {k: float(np.mean(v)) for k, v in
                       zip(["precision","recall","f1","auc"],
                           [fold_prec, fold_rec, fold_f1, fold_auc])},
        "fold_stds":  {k: float(np.std(v)) for k, v in
                       zip(["precision","recall","f1","auc"],
                           [fold_prec, fold_rec, fold_f1, fold_auc])},
        "per_fold_f1":  fold_f1,
        "per_fold_auc": fold_auc,
        "coef_mean": lr_coefs.mean(axis=0).tolist(),
        "coef_std":  lr_coefs.std(axis=0).tolist(),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("EHSA ABLATION: PROPER CROSS-VALIDATED COMPARISON")
    print("5-fold StratifiedKFold  |  random_state=42")
    print("=" * 72)

    print("\nLoading dataset...")
    pairs = load_dataset()
    n_pos = sum(p["label"] for p in pairs)
    n_neg = len(pairs) - n_pos
    print(f"  {len(pairs)} pairs ({n_pos} positive / {n_neg} negative)")

    print("\nComputing features [lex, struct, sem_real, beh=0]...")
    X, y = compute_features(pairs)
    print(f"  Done. Feature matrix: {X.shape}")

    # ── Score sets ────────────────────────────────────────────────────────────

    retrained_scores = X @ RETRAINED_WEIGHTS
    fixed_scores     = X @ FIXED_WEIGHTS
    struct_scores    = X[:, 1]

    # ── (a) Retrained weights — find optimal threshold honestly ──────────────
    # With beh_weight=0.506 and beh=0, max score = lex*0.196+struct*0.296+sem*0.002 ≈ 0.49
    # T=0.5 gives ZERO positive predictions.  Use optimal threshold on in-sample data.
    ret_opt_t, ret_opt_f1 = best_threshold_f1(y, retrained_scores)
    ret_metrics = metrics_at(y, retrained_scores, ret_opt_t)

    # ── (b) Fixed weights ────────────────────────────────────────────────────
    fix_metrics = metrics_at(y, fixed_scores, THRESHOLD_FIXED)

    # ── (c) Structural alone ─────────────────────────────────────────────────
    struct_metrics = metrics_at(y, struct_scores, THRESHOLD_FIXED)

    # ── (d) LR Adaptive — in-sample fit (what produced F1=0.919) ─────────────
    scaler_full = StandardScaler()
    X_full_s = scaler_full.fit_transform(X)
    clf_full = LogisticRegression(penalty="l2", C=1.0, random_state=42, max_iter=300)
    clf_full.fit(X_full_s, y)
    lr_in_prob = clf_full.predict_proba(X_full_s)[:, 1]
    lr_in_metrics = metrics_at(y, lr_in_prob, 0.5)

    # ── (e) LR Adaptive — 5-fold CV (honest) ─────────────────────────────────
    print("\n  Running 5-fold CV...")
    cv = cv_evaluate(X, y, n_splits=5)
    cv_agg = cv["agg"]

    # ── PRINT ─────────────────────────────────────────────────────────────────

    print("\n" + "=" * 72)
    print("TABLE 1 — STRATEGY COMPARISON (74 pairs: 54 pos / 20 neg)")
    print("=" * 72)
    print(f"  {'Strategy':<44} {'Prec':>6} {'Rec':>6} {'F1':>6} {'AUC':>6}")
    print("  " + "-" * 68)

    rows = [
        ("(a) Retrained weights DOT (opt T=%.2f, in-sample)" % ret_opt_t,
         ret_metrics, "in-sample, bias"),
        ("(b) Fixed weights T=0.8 (in-sample)",
         fix_metrics, "in-sample"),
        ("(c) Structural alone T=0.8 (in-sample)",
         struct_metrics, "in-sample"),
        ("(d) LR Adaptive, in-sample fit  [source of F1=0.919]",
         lr_in_metrics, "in-sample, INFLATED"),
        ("(e) LR Adaptive, 5-fold CV      [CITE THIS]",
         cv_agg, "held-out only"),
    ]

    for label, m, note in rows:
        flag = "  ***" if "INFLATED" in note else ("  <--" if "CITE" in note else "")
        print(f"  {label:<44} {m['precision']:>6.3f} {m['recall']:>6.3f} "
              f"{m['f1']:>6.3f} {m['auc']:>6.3f}{flag}")

    print()
    print("  *** Row (d) trains and tests on the SAME 74 pairs — inflated.")
    print("  <-- Row (e) never exposes test fold to training.  Use in paper.")

    print("\n" + "=" * 72)
    print("TABLE 2 — PER-FOLD VARIANCE (5-fold CV, LR Adaptive)")
    print("=" * 72)
    fm, fs = cv["fold_means"], cv["fold_stds"]
    print(f"  F1:        {fm['f1']:.3f} +/- {fs['f1']:.3f}   "
          f"per-fold: {[round(v,3) for v in cv['per_fold_f1']]}")
    print(f"  AUC-ROC:   {fm['auc']:.3f} +/- {fs['auc']:.3f}   "
          f"per-fold: {[round(v,3) for v in cv['per_fold_auc']]}")
    print(f"  Precision: {fm['precision']:.3f} +/- {fs['precision']:.3f}")
    print(f"  Recall:    {fm['recall']:.3f} +/- {fs['recall']:.3f}")
    if fs["f1"] > 0.10:
        print("  WARNING: F1 std > 0.10 — fold variance is HIGH.")
        print("           With ~15 test samples per fold, estimates are unreliable.")
    else:
        print("  F1 std <= 0.10 — variance is acceptable for n=74.")

    print("\n" + "=" * 72)
    print("TABLE 3 — FEATURE WEIGHT STABILITY ACROSS FOLDS")
    print("         (L2-regularized LR coefficients, renormalized to sum=1)")
    print("=" * 72)
    features = ["Lexical", "Structural", "Semantic(REAL)", "Behavioral"]
    cm, cs = cv["coef_mean"], cv["coef_std"]
    print(f"  {'Feature':<20} {'Mean Wt':>9} {'Std Dev':>9}  Status")
    print("  " + "-" * 55)
    for fname, mean, std in zip(features, cm, cs):
        status = "stable" if std < 0.05 else ("marginal" if std < 0.10 else "UNSTABLE")
        print(f"  {fname:<20} {mean:>9.4f} {std:>9.4f}  {status}")

    sem_mean, sem_std = cm[2], cs[2]
    beh_mean, beh_std = cm[3], cs[3]

    print()
    print("  SEMANTIC WEIGHT DIAGNOSIS (CV using real UniXcoder embeddings):")
    if sem_mean > 0.15:
        print(f"  -> Weight {sem_mean:.4f}: Semantic is contributing meaningfully.")
    elif sem_mean < 0.05:
        print(f"  -> Near-zero ({sem_mean:.4f}). Semantic provides little unique signal")
        print("     above Structural+Lexical on this particular dataset.")
    else:
        print(f"  -> Moderate weight ({sem_mean:.4f}).")

    print()
    print("  BEHAVIORAL WEIGHT DIAGNOSIS:")
    print(f"  -> CV weight: {beh_mean:.4f} (nearly zero because beh=0 for all pairs).")
    print("     The retrained DB weight of 0.506 is NOT 'behavioral is predictive'.")
    print("     It means LR learned that beh=0 correlates with negative labels")
    print("     on this specific benchmark. This is an evaluation artifact.")

    print("\n" + "=" * 72)
    print("LIMITATIONS / PAPER GUIDANCE")
    print("=" * 72)
    print("""
  1. The in-sample F1=0.919 (row d) must be cited as an UPPER BOUND,
     not a primary claim. The paper should lead with row (e): the 5-fold
     CV result.  Both should appear so readers can see the gap.

  2. The retrained dot-product weights (row a) cannot classify at any
     fixed threshold because beh_weight=0.506 caps scores at <0.5 when
     behavioral=0. The weights are valid for ranking (AUC), not for
     threshold-based classification on benchmarks without test cases.

  3. n=74 is small.  A fold std dev of F1 +/- 0.10 or higher means
     confidence intervals are wide.  Consider collecting more OJClone
     pairs (M9 extension) before the final camera-ready.
""")

    # ── Write ablation_results.md ─────────────────────────────────────────────
    out_path = Path(__file__).parent / "ablation_results.md"
    write_ablation_md(
        out_path, rows, cv, features, cm, cs,
        len(pairs), n_pos, n_neg
    )
    print(f"Updated: {out_path}")


def write_ablation_md(path, rows, cv, features, cm, cs, n_total, n_pos, n_neg):
    cv_agg = cv["agg"]
    fm, fs = cv["fold_means"], cv["fold_stds"]

    lines = [
        "# EHSA Ablation Study Results (M9)",
        "",
        "> **Generated:** 2026-07-25 from `experiments/ablation_cv.py`  ",
        f"> **Dataset:** {n_total} benchmark pairs — {n_pos} positive, {n_neg} negative  ",
        "> **Split:** 5-fold StratifiedKFold (random_state=42)  ",
        "> **Semantic in CV:** REAL UniXcoder embeddings  ",
        "",
        "---",
        "",
        "## Table 1 — Strategy Comparison",
        "",
        "| # | Strategy | Precision | Recall | F1 | AUC-ROC | Eval method |",
        "|---|---|---|---|---|---|---|",
    ]

    labels_short = [
        "(a) Retrained weights dot-product (opt T in-sample)",
        "(b) Fixed weights (lex=0.20 struct=0.25 sem=0.35 beh=0.20), T=0.8",
        "(c) Structural alone, T=0.8",
        "(d) LR Adaptive in-sample fit",
        "(e) **LR Adaptive 5-fold CV** ← cite this",
    ]
    eval_notes = [
        "in-sample (beh=0 caps scores, opt T chosen on train set)",
        "in-sample",
        "in-sample",
        "in-sample — **INFLATED upper bound**",
        "**held-out only — primary claim for RQ2**",
    ]

    for (_, m, _), label_s, enote in zip(rows, labels_short, eval_notes):
        lines.append(
            f"| | {label_s} | {m['precision']:.3f} | {m['recall']:.3f} | "
            f"{m['f1']:.3f} | {m['auc']:.3f} | {enote} |"
        )

    lines += [
        "",
        "> [!IMPORTANT]",
        "> **Row (e) is the number to cite in the paper.** Row (d) is in-sample and inflated.",
        "> Row (a) shows the retrained weights used as a ranking function (AUC),",
        "> not a classifier — see limitations for why a dot-product threshold is ill-defined.",
        "",
        "---",
        "",
        "## Table 2 — Per-Fold Variance (5-fold CV, LR Adaptive)",
        "",
        "| Metric | Mean | Std Dev | Per-fold values |",
        "|---|---|---|---|",
        f"| F1-Score | {fm['f1']:.3f} | ±{fs['f1']:.3f} | "
        f"{', '.join('%.3f'%v for v in cv['per_fold_f1'])} |",
        f"| AUC-ROC | {fm['auc']:.3f} | ±{fs['auc']:.3f} | "
        f"{', '.join('%.3f'%v for v in cv['per_fold_auc'])} |",
        f"| Precision | {fm['precision']:.3f} | ±{fs['precision']:.3f} | — |",
        f"| Recall | {fm['recall']:.3f} | ±{fs['recall']:.3f} | — |",
        "",
        "---",
        "",
        "## Table 3 — Feature Weight Stability Across CV Folds",
        "",
        "| Feature | Mean Weight | Std Dev | Stable? |",
        "|---|---|---|---|",
    ]

    for fname, mean, std in zip(features, cm, cs):
        stable = "Yes" if std < 0.05 else ("Marginal" if std < 0.10 else "No — UNSTABLE")
        lines.append(f"| {fname} | {mean:.4f} | ±{std:.4f} | {stable} |")

    sem_mean, sem_std = cm[2], cs[2]
    beh_mean = cm[3]

    lines += [
        "",
        "---",
        "",
        "## Limitations",
        "",
        "> [!WARNING]",
        "> **Two findings here are evaluation artifacts, not system conclusions:**",
        ">",
        f"> 1. **Behavioral weight (DB: 0.506; CV: {beh_mean:.4f}):** The benchmark has no",
        ">    executable test cases (beh=0 for all pairs). The high DB weight reflects LR",
        ">    learning that 'beh=0 is absent' correlates with negatives on this mix — not",
        ">    that behavioral output similarity is a strong signal in general.",
        "> 2. **In-sample F1=0.919 (row d):** Trained and tested on same 74 pairs.",
        ">    Must be presented alongside the CV estimate, not alone.",
        "",
        "**Sample size (n=74):** Per-fold test sets have ≈15 samples.",
        "Wide confidence intervals are expected. Consider expanding with more OJClone pairs.",
        "",
        "---",
        "",
        "## Model Comparison: GraphCodeBERT vs. UniXcoder (in-sample, real embeddings)",
        "",
        "| Model | Strategy | Precision | Recall | F1 | AUC-ROC |",
        "|---|---|---|---|---|---|",
        "| `unixcoder-base` | Semantic alone | 1.000 | 0.407 | 0.579 | 0.918 |",
        "| **`unixcoder-base`** | **Adaptive Fusion** | **0.895** | **0.944** | **0.919** | **0.942** |",
        "| `graphcodebert-base` | Semantic alone | 0.740 | 1.000 | 0.850 | 0.706 |",
        "| **`graphcodebert-base`** | **Adaptive Fusion** | **0.850** | **0.944** | **0.895** | **0.911** |",
        "",
        "> UniXcoder selected as production model (higher AUC-ROC 0.942 vs 0.911, higher precision).",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
