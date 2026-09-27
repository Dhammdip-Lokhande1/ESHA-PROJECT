# EHSA Phase 4 Transformation Classifier Evaluation Report

> **Benchmark:** TransBench-Lite Test Split
> **Total Evaluated Test Pairs:** 210
> **Rule-Based Macro F1:** 0.6897 `[0.5785, 0.7010]` | **Weighted F1:** 0.6644
> **DecisionTree Macro F1:** 0.8415 | **Weighted F1:** 0.8440

## 1. Hand-Written Rule-Based Classifier Performance

| Category | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **exact_copy** | 0.571 | 1.000 | **0.727** | 30 |
| **structural_refactoring** | 0.756 | 0.395 | **0.519** | 90 |
| **unrelated** | 1.000 | 0.744 | **0.853** | 60 |
| **variable_renaming** | 0.492 | 1.000 | **0.659** | 30 |

## 2. DecisionTree (max_depth=4) Classifier Performance

| Category | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **exact_copy** | 1.000 | 0.933 | **0.966** | 30 |
| **structural_refactoring** | 0.936 | 0.656 | **0.771** | 90 |
| **unrelated** | 1.000 | 1.000 | **1.000** | 60 |
| **variable_renaming** | 0.475 | 0.933 | **0.629** | 30 |

## 3. Extracted DecisionTree Rules

```text
|--- structural <= 0.55
|   |--- lexical <= 0.23
|   |   |--- class: unrelated
|   |--- lexical >  0.23
|   |   |--- structural <= 0.28
|   |   |   |--- class: structural_refactoring
|   |   |--- structural >  0.28
|   |   |   |--- class: unrelated
|--- structural >  0.55
|   |--- lexical <= 0.99
|   |   |--- lexical <= 0.60
|   |   |   |--- structural <= 0.93
|   |   |   |   |--- class: unrelated
|   |   |   |--- structural >  0.93
|   |   |   |   |--- class: variable_renaming
|   |   |--- lexical >  0.60
|   |   |   |--- lexical <= 0.66
|   |   |   |   |--- class: structural_refactoring
|   |   |   |--- lexical >  0.66
|   |   |   |   |--- class: structural_refactoring
|   |--- lexical >  0.99
|   |   |--- semantic <= 0.97
|   |   |   |--- semantic <= 0.39
|   |   |   |   |--- class: structural_refactoring
|   |   |   |--- semantic >  0.39
|   |   |   |   |--- class: exact_copy
|   |   |--- semantic >  0.97
|   |   |   |--- class: structural_refactoring

```

## 4. Architectural Recommendation

RECOMMENDATION: USE DECISION TREE / HYBRID ENSEMBLE.
The data-driven DecisionTree achieves Macro F1=0.8415, outperforming hand-written rules (Macro F1=0.6897).