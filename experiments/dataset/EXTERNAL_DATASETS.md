# External Research Datasets Documentation: IBM Project CodeNet (Python)

This document provides official research documentation for the external evaluation datasets used to evaluate the cross-domain generalization of EHSA's source-code similarity pipeline.

---

## 1. Internal Benchmarks vs. External Evaluation Datasets

EHSA distinguishes clearly between two distinct evaluation environments:

1. **Internal EHSA Synthetic Benchmark:** Internally constructed, lab-controlled datasets containing fine-grained code transformation categories (exact copy, variable renaming, AST refactoring, AI rewrites, hard negatives).
2. **External Evaluation Dataset (IBM Project CodeNet Subset):** EHSA was additionally evaluated on a controlled subset of IBM Project CodeNet containing 250 valid Python 3 submissions across 40 problem groups. Problem-grouped splitting was used to prevent overlap between training and external evaluation problems.

> [!IMPORTANT]
> **Complete Production Non-Interference:**
> All external evaluation workflows operate strictly within `experiments/`. Production application routes (`backend/app/`), frontend components (`frontend/`), SQLite database (`ehsa.db`), and Docker runtime remain **100% UNTOUCHED**.

---

## 2. IBM Project CodeNet (Controlled Subset Specification)

### Dataset Provenance & Citation
- **Official Title:** Project CodeNet: A Large-Scale AI for Code Dataset
- **Authors:** Ruchir Puri, David S. Kung, et al. (IBM Research)
- **Publication:** NeurIPS 2021 (Datasets and Benchmarks Track) — [arXiv:2105.12655](https://arxiv.org/abs/2105.12655)
- **Official Repository:** [https://github.com/IBM/Project_CodeNet](https://github.com/IBM/Project_CodeNet)
- **License:** Apache License 2.0
- **Subset Version:** Controlled Python Subset v1.0

### Controlled Subset Characteristics & Scope
- **Programming Language:** Native Python 3 (syntactically validated via `ast.parse`)
- **Total Selected Programs:** 250 valid Python 3 programs
- **Problem Categories:** 40 distinct competitive programming problem categories collected from AtCoder and AIZU Online Judge.
- **Ground-Truth Labeling:** Each submission is labeled with its original `problem_id`. Submissions belonging to the same `problem_id` represent **functionally related examples** written by different students to solve the exact same problem specification.

---

## 3. Experimental Setup & Leakage Prevention Protocol

### Group-Based Problem Splitting (GroupKFold)
- **Zero Problem ID Leakage:** Splitting is performed strictly by `problem_id`. Problems assigned to training folds never appear in evaluation/test folds.
- **Split Ratio:** 75% Train Problem Groups (30 problem IDs), 25% Unseen Test Problem Groups (10 problem IDs).
- **Automated Leakage Assertion:**
  ```python
  assert train_problem_ids.isdisjoint(test_problem_ids)
  ```
  *(Verified Status: **PASSED** — 0 overlapping problem IDs between train and test splits)*

### Pair Construction & Operational Labels
1. **Pairwise Functional Relatedness Classification:**
   - **Positive Pairs ($y = 1$):** Two distinct Python submissions solving the *same* problem ID ($p_A = p_B$). Operational Label: `functionally related / same problem group`.
   - **Negative Pairs ($y = 0$):** Two distinct Python submissions solving *different* problem IDs ($p_A \neq p_B$). Operational Label: `different problem groups`.
   - **Total Evaluation Pairs:** 100 balanced pairs (50 positive, 50 negative) sampled exclusively from unseen test problem groups.
2. **Code-to-Code Search Retrieval (CodeXGLUE Protocol):**
   - Evaluated via **MAP@R (Mean Average Precision at R)** across 10 query submissions (1 query per test problem group).

### Execution Safety & Static Evaluation
- **Static Multi-View Analysis:** Evaluated using EHSA's static similarity dimensions:
  - **Lexical ($S_{\text{lex}}$):** Token-level 3-gram multiset Jaccard + line diff matching.
  - **Structural ($S_{\text{struct}}$):** AST Zhang-Shasha (ZSS) tree edit distance.
  - **Semantic ($S_{\text{sem}}$):** `microsoft/unixcoder-base` 768-dimensional contextual embeddings.
  - **Research Fusion ($S_{\text{fusion}}$):** Logistic Regression trained on the 30 training problem groups.
- **Subprocess Safety:** External online-judge source programs are treated as untrusted input and restricted strictly to static analysis. Behavioral execution is NOT performed on host machines.

---

## 4. Controlled Evaluation Results Summary

| Benchmark Version | Size (# Programs / # Problems / # Pairs) | Strategy / Model | Precision | Recall | F1-Score | ROC-AUC | MAP@R |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| **Pilot Evaluation** | 50 progs / 20 probs / 10 pairs | Research Fusion | 1.000 | 0.800 | 0.889 | 1.000 | 0.625 |
| **Controlled Benchmark** | 250 progs / 40 probs / 100 pairs | Lexical Only | 0.000 | 0.000 | 0.000 | 0.881 | — |
| **Controlled Benchmark** | 250 progs / 40 probs / 100 pairs | Structural Only | 1.000 | 0.220 | 0.361 | 0.909 | — |
| **Controlled Benchmark** | 250 progs / 40 probs / 100 pairs | Semantic Only (`unixcoder`) | 0.974 | 0.740 | 0.841 | 0.928 | — |
| **Controlled Benchmark** | 250 progs / 40 probs / 100 pairs | Fixed Weight Fusion | 1.000 | 0.200 | 0.333 | 0.939 | — |
| **Controlled Benchmark** | 250 progs / 40 probs / 100 pairs | **Research Fusion (LR)** | **0.956** | **0.860** | **0.905** | **0.940** | **0.860** |

*Controlled evaluation results are persisted separately under `experiments/results/codenet_python800/controlled/`.*

---

## 5. Scientific Claim Restrictions & Guidelines

> [!IMPORTANT]
> **Strict Publication Wording Rules:**
> - **DO NOT Claim Full Dataset:** EHSA evaluated a *controlled subset* of 250 valid Python 3 programs across 40 problem groups, NOT the full multi-gigabyte CodeNet dataset.
> - **DO NOT Claim Plagiarism:** Same-problem submissions in Project CodeNet represent *functionally related competitive programming solutions*, NOT classroom plagiarism or academic dishonesty.
> - **DO Claim Generalization:** Project CodeNet demonstrates that EHSA's multi-view static similarity features generalize effectively to real-world competitive programming submissions written by independent developers.

---

## 6. Reproducibility Commands

```bash
# Step 1: Prepare problem-grouped evaluation benchmark (Random Seed = 42)
python experiments/dataset/external/codenet_python800/prepare.py

# Step 2: Execute static multi-view evaluation and generate report
python experiments/evaluate_codenet_python800.py
```
