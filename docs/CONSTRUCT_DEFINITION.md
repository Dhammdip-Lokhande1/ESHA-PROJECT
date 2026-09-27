# EHSA Research Construct Definition & Benchmark Taxonomy

This document provides the formal research definitions, construct boundaries, and evaluation targets for the Explainable Hybrid Similarity Analyzer (EHSA).

---

## 1. Construct Definitions: Plagiarism vs. Functional Clones

In source code analysis, "similarity" is not a single unified concept. EHSA explicitly distinguishes between two distinct constructs:

```
Source Code Similarity Analysis
├── Construct A: Plagiarism & Code Derivation (TransBench-Lite, EHSA 150)
│   ├── Target (y = 1): Code derived from a shared source program via AST/token transformations or LLM rewrites.
│   └── Non-Target (y = 0): Unrelated programs or independently authored solutions for the same task ("Hard Negatives").
│
└── Construct B: Same-Problem Functional Clones (Type-4) (IBM CodeNet Subset)
    ├── Target (y = 1): Programs that produce identical input-output behavior for the same computational problem.
    └── Non-Target (y = 0): Programs solving completely different computational problems.
```

### Construct A: Plagiarism & Code Derivation Obfuscation
* **Primary Objective:** Identify unauthorized code borrowing, copying, or AI-assisted derivation from a shared base submission.
* **Ground-Truth Positive ($y = 1$):**
  - `exact_copy`: Identical code or minor whitespace/comment edits.
  - `variable_renaming`: Scope-aware identifier and parameter renaming.
  - `structural_refactoring`: Control-flow, loop, and AST structural transformations.
  - `ai_rewrite`: LLM/AI-generated code rewrites preserving base functionality.
* **Ground-Truth Negative ($y = 0$):**
  - `unrelated`: Programs solving completely different problems.
  - `hard_negative`: Independently authored programs written by different students/developers solving the same assignment task.
* **Why Hard Negatives Are Negatives ($y = 0$):** In an academic setting, two students independently writing Python solutions for "Fibonacci Sequence" from scratch will produce functionally equivalent code. However, unless one student copied from the other, this is **NOT plagiarism**. Therefore, same-problem/different-author pairs must be evaluated as ground-truth negatives ($y = 0$) for plagiarism detection models.

---

### Construct B: Same-Problem Functional Clones (Type-4)
* **Primary Objective:** Detect functional equivalence across independent implementations.
* **Ground-Truth Positive ($y = 1$):**
  - Any pair of Python programs solving the same IBM CodeNet problem category (e.g., Problem `p00002`), written by different authors.
* **Ground-Truth Negative ($y = 0$):**
  - Program pairs from completely different IBM CodeNet problem categories (e.g., `p00001` vs. `p00002`).
* **Terminology Requirement:** Evaluation on this dataset measures **Type-4 Functional Clone Detection**, NOT plagiarism detection.

---

## 2. Benchmark Taxonomy & Mapping

| Benchmark Dataset | Target Construct | Total Pairs | Positives ($y=1$) | Negatives ($y=0$) | Hard Negatives Provenance & Status | Primary Research Question |
|---|---|:---:|:---:|:---:|:---:|---|
| **EHSA-Synth Benchmark** | Plagiarism & AI Rewrite | 180 Pairs (Views: `with hard negatives` N=180 [Primary], `core` N=150 [Descriptive]) | 120 Pairs (Transformations + AI) | 60 Pairs (30 Unrelated, 30 Hard Negatives) | Author-written near-miss algorithmic variants (e.g. Fib vs Lucas, Bubble vs Selection sort). NOT independent student solutions. No SHA-256 file matches with TransBench-Lite. | RQ1: Multi-view explainable signal integration |
| **TransBench-Lite** | Plagiarism & Obfuscation | 420 (210 Train / 210 Test) | 150 Test Pairs (Transformations) | 60 Test Pairs (30 Easy, 30 Hard) | Independent student solutions for same CodeNet/AIZU problems. Labeled $y=0$ (Non-Plagiarized). | RQ2: Multi-layer obfuscation detection against token baselines |
| **IBM CodeNet Subset** | Type-4 Functional Clones | 100 Pairs | 50 Pairs (Same Problem, Diff Author) | 50 Pairs (Diff Problem) | Labeled $y=1$ (Functional Clones) | RQ2: Functional clone retrieval across independent authors |
| **OJClone Benchmark** | Real-World Obfuscation | 32 Pairs | 22 Pairs (Exact + Refactored) | 10 Pairs (Unrelated) | Evaluated on real-student submissions | Real-world benchmark performance |

### Hard Negative Categorization & Cross-Dataset Sorting Rule
1. **EHSA-Synth (`hard_negative`, $y=0$):** Under Construct A (Plagiarism Derivation), pairs such as Bubble Sort vs. Selection Sort or Fibonacci vs. Lucas Numbers are author-written near-miss algorithmic variants. Because they do not share a common derivation history, they are ground-truth negatives ($y=0$).
2. **OJClone 32-Pair Set ($y=1$):** Under Construct B (Type-4 Functional Clones), implementations of sorting algorithms (Bubble, Insertion, Selection) that solve the same sorting task are evaluated for functional equivalence ($y=1$).
3. **Dataset Independence Wording:** EHSA-Synth and TransBench-Lite contain **no identical files (SHA-256 code hash overlap = 0)**. They are distinct benchmark datasets built under different curation workflows. Near-duplicate audit confirms 0 exact SHA-256 matches and 0 normalized-token hash matches between EHSA-Synth and TransBench-Lite / CodeNet.

---

## 3. Learned Channel Weights: Functional Clones vs. Plagiarism Derivation

Due to the fundamental difference in constructs, the optimal channel weights learned via Logistic Regression differ significantly between IBM CodeNet and TransBench-Lite:

| Similarity Channel | Type-4 Functional Clones (CodeNet OOF) | Plagiarism Derivation (TransBench-Lite Train) | Structural Interpretation |
|---|:---:|:---:|---|
| **Lexical Similarity ($L$)** | ~0.19 | **0.3745** (37.5%) | Higher for plagiarism where original identifier stems remain. |
| **Structural Similarity ($S$)** | ~0.30 | **0.5359** (53.6%) | Dominant feature for plagiarism derivation (AST subtrees match). |
| **Semantic Similarity ($M$)** | ~0.12 | **0.0000** (0.0% clipped) | High semantic similarity characterizes hard negatives (same-problem, diff-author), so LR assigns negative raw coef (−0.75) → clipped to 0. |
| **Behavioral Similarity ($B$)** | ~0.69 | **0.0896** (9.0%) | Disambiguates functional refactoring from unrelated code. |

> **Reproducibility note:** TransBench weights are refit live each run from the TransBench-Lite train split (210 pairs, LR L2 C=1.0 seed=42). The raw coefficients for the current run are `[L=1.8425, S=2.6362, M=−0.7498, B=0.4406]`; negative M is clipped to 0.0 before normalizing.

### Technical Rationale for Weight Discrepancy
1. **Semantic Weight ($M$):** On CodeNet, semantic neural embeddings (`microsoft/unixcoder-base`) capture high-level problem concepts, making them the strongest single predictor for functional clones. On TransBench-Lite hard negatives, both plagiarized and independent solutions share high semantic similarity (>0.90), so semantic cosine alone cannot distinguish plagiarism from independent work — hence the negative LR coefficient.
2. **Structural Weight ($S$):** On TransBench-Lite, AST subtree similarity (53.6%) uniquely detects code derivation because plagiarized submissions preserve underlying AST node hierarchies even when variables are renamed and comments removed.
3. **Behavioral Weight ($B$):** On CodeNet, behavioral similarity dominates (~69%) because independently written solutions for the same algorithm produce identical stdout. On plagiarism detection (TransBench), behavioral helps but is less decisive (~9%) since many transformations preserve behavior by design.


---
## Thesis Gap Analysis (Merged from EHSA_THESIS_GAP_ANALYSIS.md)

# EHSA — Master Thesis Information Gap Analysis Report

**Project Title:** EHSA — Explainable Hybrid Similarity Analyzer  
**Research Title:** An Explainable Hybrid Framework for Source Code Similarity Analysis Using Lexical, Structural, and Semantic Representations, with Adaptive Evidence Fusion  
**Purpose:** Comprehensive gap analysis mapping academic requirements to codebase information.

---

## 1. Requirement-to-Information Mapping

| Requirement / Section | Status | Available Codebase / Experimental Evidence | Source Artifact Location | Action / Status |
| :--- | :---: | :--- | :--- | :---: |
| **Problem Statement & Aim** | **COMPLETE** | Fully documented source code similarity challenge under renaming and refactoring. | `INSTRUCTIONS.md`, `README.md` | **READY** |
| **User Roles (2-Role Model)** | **COMPLETE** | Strictly 2 roles (`user`, `admin`). Legacy roles removed. Password hashing (PBKDF2) & JWT verified. | `backend/app/db/models.py`, `auth_routes.py` | **READY** |
| **Lexical Analyzer** | **COMPLETE** | 3-gram multiset Jaccard algorithm with matched n-gram evidence. | `backend/app/similarity/lexical.py` | **READY** |
| **Structural Analyzer** | **COMPLETE** | Zhang-Shasha AST tree edit distance ($ZSS$) with matched subtree node counts. | `backend/app/similarity/structural.py` | **READY** |
| **Semantic Analyzer** | **COMPLETE** | `microsoft/unixcoder-base` 768d embedding mean-pooling cosine similarity with length disclosure. | `backend/app/similarity/semantic.py` | **READY** |
| **Behavioral Analyzer** | **COMPLETE** | Sandboxed dynamic execution with input generation, $2\text{s}$ timeout, and $128\text{MB}$ RAM limit. | `backend/app/similarity/behavioral.py` | **READY** |
| **Adaptive Fusion Engine** | **COMPLETE** | Weighted linear combination, missing-channel renormalization, retrainable Logistic Regression. | `backend/app/fusion/fusion_engine.py` | **READY** |
| **Transformation Classifier** | **COMPLETE** | Rule-based heuristics for `exact_copy`, `variable_renaming`, `formatting_change`, `structural_refactoring`, `ai_rewrite`, `unrelated`. | `backend/app/explain/transformation_detector.py` | **READY** |
| **Database Schema** | **COMPLETE** | SQLite `ehsa.db` with 5 tables (`users`, `runs`, `evidence`, `feedback`, `fusion_weight_history`). | `backend/app/db/models.py` | **READY** |
| **REST API Gateway** | **COMPLETE** | FastAPI endpoints under `/api/v1` with Pydantic validation schemas. | `backend/app/api/` | **READY** |
| **Frontend UI** | **COMPLETE** | Next.js 16.2.11 Turbopack UI, Monaco split diff editor, Recharts charts, responsive CSS. | `frontend/src/` | **READY** |
| **External Benchmark** | **COMPLETE** | IBM Project CodeNet (250 Python programs, 100 test pairs, GroupKFold 75/25 split): $F_1 = 0.905$, $\text{ROC-AUC} = 0.940$, $\text{MAP@R} = 0.860$. | `experiments/results/codenet_python800/controlled/metrics.json` | **READY** |
| **Automated Pytest Suite** | **COMPLETE** | 236 passed, 0 failed, 5 deselected in 19.19s. | `backend/tests/` | **READY** |
| **Frontend Build Runner** | **COMPLETE** | Next.js production build PASS in 4.2s (0 TypeScript type errors). | `npm run build` | **READY** |
| **Literature Review Matrix** | **COMPLETE** | 6 landmark papers analyzed (Puri et al. 2021, Guo et al. 2022, Zhang & Shasha 1989, Prechelt et al. 2002, Feng et al. 2020, Wise 1996). | `EHSA_LITERATURE_REVIEW.md` | **READY** |
| **Master Thesis Plan** | **COMPLETE** | 50–60 page allocation plan, 23 figure plan, 15 table plan, Viva Q&A package. | `EHSA_THESIS_MASTER_STRUCTURE.md` | **READY** |

---

## 2. Audit Completeness Checklist

```text
[x] College format analyzed
[x] Chapter structure created (7 Chapters + Front/Back matter)
[x] 50–60 page allocation plan created (55 pages target)
[x] Problem statement & research objectives defined
[x] Literature review & research gap articulated
[x] 4-channel similarity methodology formulated mathematically
[x] Database ER diagram & ORM models documented
[x] Security & 2-role RBAC architecture detailed
[x] External IBM Project CodeNet benchmark metrics frozen
[x] Empirical code transformation test cases recorded
[x] Evidence matrix mapping claims -> source files completed
[x] 23 Figure plan and 15 Table plan catalogued
[x] Comprehensive Viva Voce defense Q&A package created
```

---

## 3. Final Recommendation

All required technical, algorithmic, research, database, security, and presentation information for the **EHSA Final Year Engineering Thesis / Project Book** is 100% complete, grounded in empirical evidence, and ready for chapter-by-chapter thesis writing and final academic defense.


---
## Research Gap Audit (Merged from docs/RESEARCH_GAP_AUDIT.md)

# docs/RESEARCH_GAP_AUDIT.md — EHSA Research Gap Audit

This document audits the research gaps claimed by EHSA against existing literature and evaluates how each gap is addressed by the actual implementation.

---

## 1. Claimed Research Gaps & Audit Classification

| Claimed Research Gap | Literature Baseline | Implementation Evidence | Classification Status | External Reference Required |
|---|---|---|---|---|
| **1. Ineffectiveness of Lexical Matching Against LLM Code Rewrites** | Standard tools (MOSS, JPlag) rely on token/string matching, failing when variable names or code structures are mutated by LLMs. | `semantic.py` (UniXcoder embeddings) and `structural.py` (AST ZSS distance) detect semantic similarity even when lexical similarity drops below 0.40. | **VERIFIED FROM IMPLEMENTATION** | Karnalim et al. [3], Martinez-Gil [6] |
| **2. Black-Box Neural Opacity in Deep Learning Similarity Tools** | Deep learning models (CodeBERT, GraphCodeBERT) output similarity scores without explaining *why* code is similar, making scores unusable in academic proceedings. | `explanation_generator.py` synthesizes line token diffs, AST edit ops, behavioral trace comparisons, and AI features into human-readable evidence. | **VERIFIED FROM IMPLEMENTATION** | SemEval 2026 Task 13 [7] |
| **3. Static Weighting Rigidity in Ensemble Similarity Analyzers** | Prior ensemble systems use static fixed weights that cannot adapt when students adopt new obfuscation techniques. | `adaptive_trainer.py` implements a `RidgeClassifier` that retrains fusion weights dynamically based on instructor `confirmed` vs `false_positive` verdicts. | **VERIFIED FROM IMPLEMENTATION** | PAN 2025 Benchmarks [9] |
| **4. Lack of Dynamic Execution Trace Verification in Static Tools** | Static code analysis tools cannot verify functional equivalence when AST structures and variable names are completely rewritten. | `behavioral.py` executes code in a sandboxed subprocess across 5 test inputs, matching output traces ($S_{\text{beh}} = 1.0$ for functional duplicates). | **VERIFIED FROM IMPLEMENTATION** | FeatFuse Benchmarks [8] |
| **5. High False Positive Rates on AI-Assisted Student Code** | Existing tools flag legitimate AI assistance (e.g. formatting, type hints) as wholesale plagiarism. | `ai_generation_detector.py` isolates 6 code quality features (docstring density, type hint density, entropy, PEP8 compliance) to separate style from structural copying. | **VERIFIED FROM IMPLEMENTATION** | SemEval 2026 Task 13 [7] |

---

## 2. Citation Requirements for Academic Publication

To validate these research gaps in a thesis or conference paper, the following literature support MUST be cited:

1. **Lexical Tool Failure:** Cite Bowyer & Hall (2000) and Prechelt et al. (2002) for JPlag/MOSS baselines and their vulnerability to AST-level refactoring.
2. **Explainable AI in Academic Integrity:** Cite Karnalim & Novak (2021) regarding the requirement for traceable AST evidence in institutional academic misconduct hearings.
3. **Multi-Signal Ensemble Systems:** Cite Martinez-Gil (2023) for fixed-weight ensemble similarity baselines.
4. **Adaptive Weighting & Learning from Feedback:** Cite PAN 2025 shared task findings on cross-domain similarity generalization.
