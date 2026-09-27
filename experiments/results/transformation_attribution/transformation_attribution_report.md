# EHSA Phase 4 Transformation Attribution & Evidence Quality Report

> **Benchmark:** TransBench-Lite Test Split
> **Total Evaluated Pairs:** 210
> **Macro F1-Score:** 0.5199 | **Weighted F1-Score:** 0.6146
> **Expected Calibration Error (ECE):** 0.2602
> **Evidence Completeness Rate:** 100.00%

## 1. Per-Class Transformation Classification Metrics

| Category | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **exact_copy** | 0.588 | 1.000 | **0.741** | 30 |
| **partial_match** | 0.000 | 0.000 | **0.000** | 0 |
| **structural_refactoring** | 0.756 | 0.378 | **0.504** | 90 |
| **unrelated** | 1.000 | 0.533 | **0.696** | 60 |
| **variable_renaming** | 0.492 | 1.000 | **0.659** | 30 |

## 2. Confusion Matrix

| Expected \ Predicted | exact_copy | partial_match | structural_refactoring | unrelated | variable_renaming |
|---|---|---|---|---|---|
| **exact_copy** | 30 | 0 | 0 | 0 | 0 |
| **partial_match** | 0 | 0 | 0 | 0 | 0 |
| **structural_refactoring** | 21 | 4 | 34 | 0 | 31 |
| **unrelated** | 0 | 17 | 11 | 32 | 0 |
| **variable_renaming** | 0 | 0 | 0 | 0 | 30 |

## 3. Confidence Calibration Bins (ECE)

| Confidence Bin | Count | Avg Confidence | Avg Accuracy | Absolute Error |
|---|---|---|---|---|
| `[0.0, 0.2]` | 52 | 0.0555 | 0.6538 | 0.5984 |
| `[0.2, 0.4]` | 18 | 0.3234 | 0.5000 | 0.1766 |
| `[0.4, 0.6]` | 22 | 0.4711 | 0.9545 | 0.4834 |
| `[0.6, 0.8]` | 35 | 0.7365 | 1.0000 | 0.2635 |
| `[0.8, 1.0]` | 83 | 0.9459 | 0.9518 | 0.0059 |

## 4. Evidence Quality & Explanation Audit Summary

- **Completeness Rate:** `100.00%` of test predictions contained fully-structured explanations with non-empty supporting evidence.
- **Rule Match Fidelity:** 100% of generated explanations explicitly cited exact numeric similarity values driving the rule decision.
- **Advisory Language Scoping:** 100% of explanations incorporated non-absolute, investigative advisory disclaimers.