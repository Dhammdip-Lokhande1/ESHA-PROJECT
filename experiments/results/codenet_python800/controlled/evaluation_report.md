# IBM Project CodeNet (Python800) External Evaluation Report

> **Official Source:** IBM Research (Puri et al., NeurIPS 2021) / GitHub: IBM/Project_CodeNet  
> **Dataset License:** Apache License 2.0  
> **Evaluation Size:** 100 pairs across 10 unseen problem groups  
> **Leakage Prevention:** Deterministic GroupKFold by problem_id (Zero Problem Leakage across splits)  

---

## 1. Global Performance Comparison

| Component / Strategy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|
| **Lexical Only** | 0.000 | 0.000 | 0.000 | 0.881 |
| **Structural Only** | 1.000 | 0.220 | 0.361 | 0.909 |
| **Semantic Only** | 0.974 | 0.740 | 0.841 | 0.928 |
| **Fixed Weight Fusion** | 1.000 | 0.200 | 0.333 | 0.939 |
| **Research Fusion (Logistic Regression)** | 0.956 | 0.860 | 0.905 | 0.940 |

---

## 2. Code-to-Code Search Retrieval Metric

- **MAP@R (Mean Average Precision at R):** `0.860`

---

## 3. Learned Signal Importance (Research-Side Fusion)

- **Lexical Weight:** `0.1918`
- **Structural Weight:** `0.3324`
- **Semantic Weight:** `0.4758`

---

## 4. Key Research Findings & Isolation Confirmation
- **External Generalization:** EHSA's static multi-signal architecture demonstrates strong generalization on unseen IBM Project CodeNet Python competitive programming submissions.
- **Zero Production Touch:** All evaluations were performed isolated under `experiments/` without modifying FastAPI backend routes, Next.js frontend pages, SQLite schemas, or production fusion weights.
- **Zero Data Leakage:** Group-based problem splitting guarantees test submissions solve problem IDs never seen during training.