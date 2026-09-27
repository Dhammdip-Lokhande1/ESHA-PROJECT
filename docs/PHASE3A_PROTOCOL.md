# PHASE 3A EVALUATION PROTOCOL

**EHSA Explainable Hybrid Similarity Analyzer**  
**Version:** 2.0 — Phase 3A External Baseline Evaluation  
**Date:** 2026-09-21  
**Status:** Authoritative (replaces all prior draft protocol notes)

---

## 1. Purpose

This document defines the complete, reproducible evaluation protocol for Phase 3A:
External Baseline Evaluation with Statistical Significance Testing.

It covers:
- Data splits and labeling policy for every benchmark
- Metrics computed and how they are derived
- Which methods are evaluated and how inference is performed
- What constitutes a "score" (must be continuous; no binary reconstruction)
- Statistical test procedure and correction policy

---

## 2. Datasets and Splits

### 2.1 EHSA Research Benchmark — Core 150 Pairs

| Property | Value |
|---|---|
| Source | Hand-curated by researchers from Python course submissions (anonymized) |
| Total pairs | 150 |
| Split | No train/test split; 5-fold Group Cross-Validation for EHSA fusion |
| Positives ($y=1$) | 120 pairs (4 transformation categories × 30 pairs each) |
| Negatives ($y=0$) | 30 pairs (unrelated programs, different problem domain) |
| Group key | `source_program_id` (base program each pair derives from) |
| Hard negatives | **Excluded** from this 150-pair core set |
| Script | `experiments/stats_tests.py` (Section 1) |
| Results file | `experiments/results/statistical_tests.json` → `EHSA_Benchmark_150_Core` |

**Category label mapping:**

| Category | Label | Count |
|---|:---:|:---:|
| `exact_copy` | 1 (positive) | 30 |
| `variable_renaming` | 1 (positive) | 30 |
| `structural_refactoring` | 1 (positive) | 30 |
| `ai_rewrite` | 1 (positive) | 30 |
| `unrelated` | 0 (negative) | 30 |

---

### 2.2 EHSA Research Benchmark — Expanded 180 Pairs

| Property | Value |
|---|---|
| Source | Core 150 pairs + 30 hard negatives (same-problem/different-author) |
| Total pairs | 180 |
| Positives ($y=1$) | 120 (same as Core 150) |
| Negatives ($y=0$) | 60 (30 unrelated + 30 hard_negative) |
| Group key | `source_program_id` |
| Hard negatives | **Included** and labeled $y=0$ (see CONSTRUCT_DEFINITION.md §1) |
| Script | `experiments/stats_tests.py` (Section 1b) |
| Results file | `experiments/results/statistical_tests.json` → `EHSA_Benchmark_180_Expanded` |

**Hard-negative false positive rate** is reported separately per method to show
how often EHSA incorrectly flags independent same-problem solutions as plagiarism.

---

### 2.3 TransBench-Lite — Test Split 210 Pairs

| Property | Value |
|---|---|
| Source | Synthetic transformation benchmark, 7 transformation families |
| Total pairs | 420 (210 train + 210 test); evaluation is on **test split only** |
| Positives ($y=1$) | 150 test pairs (5 families × 30 pairs each) |
| Negatives ($y=0$) | 60 test pairs (30 easy negatives + 30 hard negatives) |
| Group key | `problem_id` (base program) |
| Fusion weights | **Learned from TransBench train split** via LR (L2, C=1.0, seed=42); see §4 |
| Script | `experiments/stats_tests.py` (Section 2) |
| Results file | `experiments/results/statistical_tests.json` → `TransBench_Lite_210` |

**7 transformation families (labels → split assignment):**

| Family | Type | Label |
|---|---|:---:|
| `exact_copy` | Positive | 1 |
| `variable_renaming` | Positive | 1 |
| `structural_refactoring` | Positive | 1 |
| `dead_code_insertion` | Positive | 1 |
| `combined` | Positive | 1 |
| `easy_negative` (different problem) | Negative | 0 |
| `hard_negative` (same problem, different author) | Negative | 0 |

**Cross-validation note:** The TransBench 200/210 accuracy figure reported in
`evaluate_transformation_cls.py` refers to the **transformation classifier**
(predicting *which* transformation was applied), not the binary similarity model.
That classifier uses LOOCV grouped by base program. These are distinct tasks.

---

### 2.4 IBM CodeNet Controlled Subset — 100 Pairs

| Property | Value |
|---|---|
| Source | IBM CodeNet Python submissions (subset of `codenet_python800`) |
| Total pairs | 100 |
| Positives ($y=1$) | 50 (same problem, different author — Functional Clone, Type-4) |
| Negatives ($y=0$) | 50 (different problem entirely) |
| Group key | `problem_id_a` |
| EHSA fusion | OOF Group-CV (GroupKFold=5, grouped by `problem_id_a`) on real scores |
| Score source | **Real EHSA scores** from `pair_cache.pkl` (all 100 pairs cached) |
| Score type | 3-tuple (L,S,M) for 88 pairs; 5-tuple (L,S,M,B,exec) for 12 pairs |
| Behavioral imputation | 0.5 (not label-derived) for 3-tuple pairs |
| Script | `experiments/stats_tests.py` (Section 3) |
| Results file | `experiments/results/statistical_tests.json` → `CodeNet_100` |

> **IMPORTANT — Construct difference:** CodeNet evaluates **Type-4 Functional
> Clone Detection** (same problem, different independent author). This is NOT
> the same construct as plagiarism detection. Results on CodeNet MUST NOT be
> cited as "plagiarism detection accuracy." See `docs/CONSTRUCT_DEFINITION.md`.

---

### 2.5 OJClone Algorithmic Benchmark — 32 Pairs

| Property | Value |
|---|---|
| Source | Hand-written textbook algorithmic Python pairs across 5 task categories |
| Total pairs | 32 |
| Positives ($y=1$) | 22 (`exact_copy` + `structural_refactoring`) |
| Negatives ($y=0$) | 10 (unrelated tasks) |
| Group key | Task name (factorial, fibonacci, sorting, prime_check, binary_search) |
| Score source | **Real EHSA pipeline** computed fresh from `.py` files (no cache) |
| Behavioral | `behavioral_similarity` module called live on each pair |
| Script | `experiments/stats_tests.py` (Section 4) + `experiments/evaluate_ojclone.py` |
| Results file | `experiments/results/statistical_tests.json` → `OJClone_32` |

> **IMPORTANT — Provenance claim:** This is Type-4 functional clone detection
> (are these algorithmically equivalent?), not plagiarism detection. Do not
> conflate with TransBench or EHSA-150 results.

---

## 3. Metrics

### 3.1 Threshold-Based Metrics (τ = 0.50)

All threshold-based metrics are computed from integer confusion counts **only**.
No floating-point metric is written by hand. Every metric is asserted to
match its integer-count formula within ε < 1e-4.

| Metric | Formula (integer counts) |
|---|---|
| Precision | TP / (TP + FP); 0 if TP + FP = 0 |
| Recall (Sensitivity) | TP / (TP + FN); 0 if TP + FN = 0 |
| F1-Score | 2·P·R / (P + R); 0 if P + R = 0 |
| Accuracy | (TP + TN) / N |
| Balanced Accuracy | 0.5 · (TP/(TP+FN) + TN/(TN+FP)) |
| MCC | from `sklearn.metrics.matthews_corrcoef` (verified against formula) |

### 3.2 Ranking Metrics (Continuous Scores Required)

| Metric | Requirement |
|---|---|
| ROC-AUC | Computed from **continuous** float similarity scores, not binary predictions |
| PR-AUC | Computed from `precision_recall_curve` then `auc(recall, precision)` |
| F1 95% CI | Group-level bootstrap (500 resamples, groups = task/problem_id) |
| AUC 95% CI | Group-level bootstrap (500 resamples) |

> **ENFORCEMENT:** `evaluate_dataset_stats()` asserts `len(np.unique(sc)) > 2`
> for every score vector passed to `roc_auc_score`. This prevents accidentally
> computing AUC from thresholded binary predictions (which reduces to balanced
> accuracy). Any violation raises `AssertionError` and halts the pipeline.

---

## 4. Inference and Score Computation

### 4.1 EHSA Multi-View Fusion Scores

**On EHSA-150 (Core) and EHSA-180 (Expanded):**
- 5-fold GroupKFold CV on `source_program_id`
- For each fold: StandardScaler + LR(L2, C=1.0, seed=42) fit on train
- OOF probabilities (`predict_proba[:, 1]`) used as continuous scores
- **No test-set contamination:** each pair's score uses model trained without it

**On TransBench-Lite Test Split:**
- LR trained on TransBench **train split only** (210 pairs)
- Raw LR coefficients printed to console each run (reproducible from cache)
- Negative coefficients clipped to 0.0, then normalized to sum-to-1 weights
- Weighted fusion score: `w_L·L + w_S·S + w_M·M + w_B·B`
- These weights are NOT tuned on the test split

**On IBM CodeNet:**
- 5-fold GroupKFold CV on `problem_id_a`
- Same OOF LR procedure as EHSA-150

**On OJClone-32:**
- Direct weighted fusion using TransBench-derived weights (from train split)
- No additional training on OJClone data

### 4.2 Baseline Score Computation

| Method | Score Definition |
|---|---|
| Semantic-Only (UniXcoder) | Raw cosine similarity from `semantic_similarity()` |
| JPlag/MOSS Token Baseline | `normalized_token_baseline()` from `experiments/baselines.py` |
| Lexical-Only | Normalized Levenshtein + token Jaccard from `lexical_similarity()` |
| Structural-Only | Zhang-Shasha tree edit distance on AST from `structural_similarity()` |

All baseline scores are continuous floats in [0, 1]. No thresholding before AUC.

### 4.3 Score Provenance Rules (NON-NEGOTIABLE)

1. **No label-derived scores:** score arrays must not be constructed from `np.where(y==1)` or similar label-dependent operations. Score for pair i is computed from code_a_i and code_b_i only.
2. **No confusion-matrix reconstruction:** scores must not be reconstructed from TP/FP/FN/TN counts + noise. The score for pair i must be the actual model output.
3. **No constant imputation for the EHSA method:** if the full pipeline (including behavioral) cannot produce a score for a pair, that pair is marked `UNSCORED` and excluded from evaluation, rather than imputed from the label.
4. **Behavioral imputation (0.5) applies only to baselines and non-primary datasets** where behavioral execution was not performed. The canonical EHSA-150 evaluation uses 5-tuple cache entries (all pairs executed).

---

## 5. Statistical Testing

### 5.1 McNemar Exact Test (Pairwise)

- Test: EHSA vs. each baseline on the same binary predictions at τ=0.5
- Statistic: b = pairs where EHSA correct, baseline wrong; c = reverse
- p-value: 2 × Binomial.CDF(min(b,c), b+c, 0.5); clipped to [0, 1]
- Null hypothesis: the two methods have the same error rate

### 5.2 Holm-Bonferroni Correction

- Applied **within each dataset separately** (not pooled across datasets)
- Controls Family-Wise Error Rate (FWER) at α = 0.05
- Step-down: sort raw p-values ascending; multiply by (m, m-1, ..., 1); take running max

### 5.3 Group-Level Bootstrap CIs (95%)

- 500 resamples (each resample: sample unique groups with replacement)
- Per resample: compute F1 and AUC on all pairs belonging to sampled groups
- 2.5th and 97.5th percentile = 95% CI
- Groups: `source_program_id` (EHSA/TransBench), `problem_id_a` (CodeNet), task name (OJClone)

---

## 6. Output Files

| File | Contents |
|---|---|
| `experiments/results/statistical_tests.json` | Master results: all datasets, all methods, all metrics, McNemar p-values, Holm-adjusted p, bootstrap CIs |
| `experiments/results/statistical_tests_report.md` | Human-readable table generated from `statistical_tests.json` |
| `experiments/results/ojclone32/metrics.json` | OJClone-specific results from `evaluate_ojclone.py` |
| `experiments/results/baselines_ablation/metrics.json` | 15-channel ablation results from `evaluate_baselines.py` |
| `experiments/results/transformation_cls/` | Transformation classifier results from `evaluate_transformation_cls.py` |

---

## 7. Open Issues and Known Limitations

| Issue | Status | Action |
|---|---|---|
| OJClone behavioral scores | REAL — behavioral_similarity called live | Verified in Section 4.1 |
| CodeNet behavioral imputed to 0.5 (88/100 pairs) | KNOWN LIMITATION | Reported in results; does not affect L/S/M scores |
| TransBench weights (0.3323/0.5302/0.0000/0.1375) stale | FIXED — now refit live from train split each run | See Section 4.1 |
| CodeNet synthetic placeholder scores | FIXED — now uses real cache scores + OOF LR | See §2.4 |
| OJClone TP/FP/FN noise reconstruction | FIXED — now uses real EHSA pipeline | See §2.5 |
| AI detector evaluation | UNRESOLVED — needs 50-100 real LLM rewrite pairs | Mark as future work |
| User study (RQ4) | UNRESOLVED — no real instructor study data | Remove RQ4 or label simulated |
| Significance tests: all results NS at α=0.05 | Known; dataset sizes limit power | Report effect sizes (ΔF1, ΔAUC) with CIs |
