# EHSA Statistical Significance & Evaluation Report

> **Methodology:** Group-Level Bootstrap CIs (500 resamples), Exact Group-Level McNemar Binomial Tests ($b$ vs. $c$ outcome disagreements), and Holm-Bonferroni Step-Down Correction per dataset.
> **Continuous Score Rule:** All ROC-AUC metrics calculated directly from continuous float similarity scores (not binary step predictions).
> **EHSA-Synth Specification:** Single unified benchmark (N=180) evaluated under 'core' (N=150) and 'with hard negatives' (N=180) views, with 0 code hash leakage across 5-fold CV.

---

## EHSA-Synth Per-Category Performance Breakdown

| Category | Type | EHSA Multi-View Fusion | Semantic-Only (UniXcoder) | JPlag/MOSS Token Baseline | Lexical-Only | Structural-Only |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **exact_copy** | Positive (Recall) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **variable_renaming** | Positive (Recall) | 1.0000 | 0.9333 | 1.0000 | 0.0000 | 1.0000 |
| **structural_refactoring** | Positive (Recall) | 0.9333 | 1.0000 | 0.0667 | 0.0333 | 0.3000 |
| **ai_rewrite** | Positive (Recall) | 0.8000 | 0.8333 | 0.0000 | 0.0000 | 0.0667 |
| **unrelated** | Negative (FPR) | 0.1000 | 0.1000 | 0.0000 | 0.0000 | 0.0667 |
| **hard_negative** | Negative (FPR) | 0.6667 | 0.6667 | 0.1667 | 0.1667 | 0.4000 |

### Primary Metric: AUC of Positives vs. Hard Negatives
**Primary Metric AUC (120 Positives vs 30 Hard Negatives):**

- **EHSA Multi-View Fusion**: `0.7256`
- **Semantic-Only (UniXcoder)**: `0.7267`
- **JPlag/MOSS Token Baseline**: `0.6521`
- **Lexical-Only**: `0.5744`
- **Structural-Only**: `0.6540`

---

## EHSA-Synth View: CORE (N=150, Groups=5)

| Method | Precision | Recall | F1-Score [95% Group CI] | MCC | Bal Acc | ROC-AUC [95% Group CI] | McNemar Raw $p$ | Holm-Adjusted $p$ | Significant ($lpha=0.05$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EHSA Multi-View Fusion** | 0.9739 | 0.9333 | 0.9532 `[0.923, 0.975]` | 0.7881 | 0.9167 | 0.9733 `[0.938, 0.994]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Semantic-Only (UniXcoder)** | 0.9741 | 0.9417 | 0.9576 `[0.924, 0.986]` | 0.8041 | 0.9208 | 0.9819 `[0.956, 0.996]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **JPlag/MOSS Token Baseline** | 1.0000 | 0.5167 | 0.6813 `[0.667, 0.696]` | 0.4197 | 0.7583 | 0.7893 `[0.735, 0.844]` | `5.5196e-12` | `1.6559e-11` | **YES** |
| **Lexical-Only** | 1.0000 | 0.2583 | 0.4106 `[0.400, 0.431]` | 0.2552 | 0.6292 | 0.9758 `[0.944, 0.996]` | `1.0221e-20` | `4.0885e-20` | **YES** |
| **Structural-Only** | 0.9726 | 0.5917 | 0.7358 `[0.698, 0.769]` | 0.4201 | 0.7625 | 0.7983 `[0.750, 0.841]` | `4.6219e-10` | `9.2439e-10` | **YES** |

---

## EHSA-Synth View: WITH_HARD_NEGATIVES (N=180, Groups=5)

| Method | Precision | Recall | F1-Score [95% Group CI] | MCC | Bal Acc | ROC-AUC [95% Group CI] | McNemar Raw $p$ | Holm-Adjusted $p$ | Significant ($lpha=0.05$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EHSA Multi-View Fusion** | 0.8296 | 0.9333 | 0.8784 `[0.825, 0.930]` | 0.5988 | 0.7750 | 0.8494 `[0.777, 0.902]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Semantic-Only (UniXcoder)** | 0.8309 | 0.9417 | 0.8828 `[0.835, 0.922]` | 0.6124 | 0.7792 | 0.8543 `[0.781, 0.907]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **JPlag/MOSS Token Baseline** | 0.9254 | 0.5167 | 0.6631 `[0.642, 0.684]` | 0.4226 | 0.7167 | 0.7207 `[0.676, 0.768]` | `1.3084e-04` | `2.6168e-04` | **YES** |
| **Lexical-Only** | 0.8611 | 0.2583 | 0.3974 `[0.377, 0.423]` | 0.2062 | 0.5875 | 0.7751 `[0.670, 0.874]` | `1.0115e-10` | `4.0460e-10` | **YES** |
| **Structural-Only** | 0.8353 | 0.5917 | 0.6927 `[0.647, 0.737]` | 0.3384 | 0.6792 | 0.7262 `[0.656, 0.792]` | `1.4013e-05` | `4.2039e-05` | **YES** |

---

## TransBench-Lite Test Split 210 (N=210, Groups=37)

| Method | Precision | Recall | F1-Score [95% Group CI] | MCC | Bal Acc | ROC-AUC [95% Group CI] | McNemar Raw $p$ | Holm-Adjusted $p$ | Significant ($lpha=0.05$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EHSA Full Model (L+S+M+B)** | 0.9615 | 1.0000 | 0.9804 `[0.967, 0.994]` | 0.9303 | 0.9500 | 1.0000 `[1.000, 1.000]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Semantic-Only Baseline** | 0.8144 | 0.9067 | 0.8580 `[0.830, 0.881]` | 0.4366 | 0.6950 | 0.7438 `[0.655, 0.849]` | `3.8199e-11` | `1.5280e-10` | **YES** |
| **JPlag/MOSS Token Baseline** | 1.0000 | 0.9933 | 0.9967 `[0.988, 1.000]` | 0.9885 | 0.9967 | 0.9996 `[0.998, 1.000]` | `1.2500e-01` | `1.2500e-01` | NO (NS) |
| **Lexical-Only Baseline** | 1.0000 | 0.6467 | 0.7854 `[0.686, 0.870]` | 0.5860 | 0.8233 | 0.9686 `[0.939, 0.993]` | `1.7539e-10` | `5.2618e-10` | **YES** |
| **Structural-Only Baseline** | 0.8982 | 1.0000 | 0.9464 `[0.915, 0.973]` | 0.8023 | 0.8583 | 0.9961 `[0.991, 1.000]` | `9.7656e-04` | `1.9531e-03` | **YES** |

---

## IBM CodeNet Controlled Subset 100 (N=100, Groups=10)

| Method | Precision | Recall | F1-Score [95% Group CI] | MCC | Bal Acc | ROC-AUC [95% Group CI] | McNemar Raw $p$ | Holm-Adjusted $p$ | Significant ($lpha=0.05$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EHSA Multi-View Fusion (OOF)** | 0.9000 | 0.9000 | 0.9000 `[0.828, 0.952]` | 0.8000 | 0.9000 | 0.9256 `[0.851, 0.987]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Semantic-Only (UniXcoder)** | 0.8936 | 0.8400 | 0.8660 `[0.744, 0.950]` | 0.7413 | 0.8700 | 0.9280 `[0.856, 0.988]` | `5.0781e-01` | `5.0781e-01` | NO (NS) |
| **JPlag/MOSS Token Baseline** | 1.0000 | 0.0800 | 0.1481 `[0.000, 0.276]` | 0.2041 | 0.5400 | 0.8468 `[0.697, 0.959]` | `4.4059e-08` | `1.3218e-07` | **YES** |
| **Lexical-Only** | 0.0000 | 0.0000 | 0.0000 `[0.000, 0.000]` | 0.0000 | 0.5000 | 0.8808 `[0.760, 0.965]` | `4.2099e-09` | `1.6839e-08` | **YES** |
| **Structural-Only** | 0.9048 | 0.3800 | 0.5352 `[0.403, 0.658]` | 0.4174 | 0.6700 | 0.8648 `[0.802, 0.933]` | `1.5236e-05` | `3.0473e-05` | **YES** |

---

## Python Textbook Algorithmic Refactoring Benchmark (32 Pairs) (N=32, Groups=5)

| Method | Precision | Recall | F1-Score [95% Group CI] | MCC | Bal Acc | ROC-AUC [95% Group CI] | McNemar Raw $p$ | Holm-Adjusted $p$ | Significant ($lpha=0.05$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fusion (TransBench Weights)** | 1.0000 | 0.5455 | 0.7059 `[0.624, 0.800]` | 0.5222 | 0.7727 | 0.7955 `[0.644, 0.921]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Semantic-Only (UniXcoder)** | 0.8947 | 0.7727 | 0.8293 `[0.581, 0.939]` | 0.5405 | 0.7864 | 0.8818 `[0.852, 0.932]` | `4.5312e-01` | `1.0000e+00` | NO (NS) |
| **JPlag/MOSS Token Baseline** | 1.0000 | 0.5455 | 0.7059 `[0.624, 0.800]` | 0.5222 | 0.7727 | 0.7955 `[0.700, 0.881]` | `1.0000e+00` | `1.0000e+00` | NO (NS) |
| **Lexical-Only** | 1.0000 | 0.4545 | 0.6250 `[0.543, 0.733]` | 0.4545 | 0.7273 | 0.7864 `[0.725, 0.889]` | `5.0000e-01` | `1.0000e+00` | NO (NS) |
| **Structural-Only** | 0.8571 | 0.5455 | 0.6667 `[0.500, 0.763]` | 0.3228 | 0.6727 | 0.8000 `[0.644, 0.914]` | `5.0000e-01` | `1.0000e+00` | NO (NS) |

---
