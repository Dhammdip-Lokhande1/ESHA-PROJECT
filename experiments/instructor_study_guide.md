# EHSA Instructor User Study Protocol & Evaluation Guide

> **Notice:** This document defines the protocol, task script, evaluation dataset, and data collection schema for conducting the real human instructor user study for Milestone 10.

---

## 1. Study Objective & Research Hypothesis (RQ3)

- **Objective:** Evaluate whether presenting fine-grained, evidence-grounded explanations (AST subtree diffs, token n-gram matches, semantic disclosures, behavioral execution logs) improves instructor decision confidence and trust compared to presenting a bare numerical similarity score alone.
- **Research Question (RQ3):** Does evidence-grounded explanation improve instructor understanding and decision confidence compared to score-only baselines?
- **Hypothesis $H_1$:** Instructors evaluating code pairs with full explainable evidence will report significantly higher decision confidence ($p < 0.05$, Wilcoxon signed-rank test) than when evaluating with score-only output.

---

## 2. Experimental Design

- **Design:** Within-subject paired trial ($N \ge 5\text{--}8$ human computer science instructors/TAs).
- **Conditions:**
  1. **Control (Score-Only):** Instructor is shown only the overall numerical similarity percentage (e.g. `82% similarity`).
  2. **Treatment (Full Explanation):** Instructor is shown the full EHSA dashboard containing score cards, transformation type badge, expandable evidence panels, and plain-language explanation text.

---

## 3. Evaluation Dataset (Real Benchmark Pairs)

The study uses 5 specific code submission pairs selected from the EHSA benchmark dataset:

| Pair ID | Dataset Source | Target Transformation Type | Purpose |
|---|---|---|---|
| **Pair 1** | `experiments/dataset/pair1` | `exact_copy` | Verifies confidence on straightforward identical matches |
| **Pair 2** | `experiments/dataset/pair2` | `variable_renaming` | Tests detection of identifier obfuscation |
| **Pair 3** | `experiments/dataset/pair3` | `structural_refactoring` | Tests detection of loop/control flow refactoring |
| **Pair 4** | `experiments/dataset/ojclone/oj_1` | `OJClone Real Submission` | Tests evaluation on real student problem submissions |
| **Pair 5** | `experiments/dataset/pair5` | `unrelated` | Verifies false-positive rejection confidence |

---

## 4. Participant Task Script

1. **Briefing (2 mins):** Explain that the instructor will inspect 5 pairs of student Python submissions to judge whether potential code reuse / plagiarism occurred.
2. **Task Execution (15 mins):**
   - For each pair, the instructor reviews the code in **Condition A (Score-Only)** and records their confidence (1–5 scale).
   - The instructor then reviews the same pair in **Condition B (Full Explanation)** and records their confidence (1–5 scale).
3. **Survey Questions (1–5 Likert Scale):**
   - **Q1 (Confidence):** *How confident are you in your judgment for this code pair?* (1 = Very Low, 5 = Very High)
   - **Q2 (Usefulness):** *How useful was the evidence panel (AST diff / token matches / behavioral log) in making your decision?* (1 = Not Useful, 5 = Extremely Useful)
   - **Q3 (Trust):** *How much do you trust the system's explanation for this pair?* (1 = No Trust, 5 = Complete Trust)

---

## 5. Data Collection Schema

Responses from real human participants must be logged directly into `experiments/user_study_data.csv` using the following schema:

```csv
participant_id,pair_id,condition,confidence_score,usefulness_score,trust_score
P1,pair1,score_only,3,,
P1,pair1,explainable,5,5,4
P1,pair2,score_only,2,,
P1,pair2,explainable,4,4,4
...
```

A clean template file is provided at `experiments/user_study_template.csv`.
