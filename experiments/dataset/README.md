# EHSA Research-Grade Code Similarity Benchmark Dataset (v1.0)

## Overview

This directory contains the **EHSA Research Benchmark Dataset**, a controlled, 150-pair code similarity evaluation suite designed for explainable multi-view source-code similarity investigation in Python.

It evaluates EHSA across four distinct code transformation techniques and one control category of unrelated code.

---

## Dataset Structure

```
experiments/dataset/
├── README.md                  # Dataset documentation & reproducibility guide
├── dataset_card.md            # Research-grade dataset card
├── metadata.csv               # Complete metadata table for all 150 pairs
├── labels.csv                 # Binary ground-truth labels (for legacy runners)
├── validation_report.json     # Automated quality & integrity report
├── pairs/                     # Individual pair directories (150 folders)
│   ├── P001_EXACT/
│   │   ├── code_a.py
│   │   ├── code_b.py
│   │   └── metadata.json
│   ├── P001_VAR/
│   ├── P001_STRUCT/
│   ├── P001_AI/
│   └── P001_UNREL/
├── splits/                    # 5-fold grouped cross-validation splits
│   ├── fold_1.csv
│   ├── fold_2.csv
│   ├── fold_3.csv
│   ├── fold_4.csv
│   └── fold_5.csv
└── provenance/
    └── sources.csv            # Original source program descriptions & licensing
```

---

## Dataset Composition

- **Total Unique Pairs:** 150
- **Source Program Groups:** 30 (`P001` through `P030`)
- **Categories (30 pairs per category):**
  1. `exact_copy` (Label 1): Identical / comment & formatting variations
  2. `variable_renaming` (Label 1): Identifier and parameter renaming
  3. `structural_refactoring` (Label 1): Control-flow / AST structure transformations
  4. `ai_rewrite` (Label 1): Idiomatic / Pythonic library rewrites
  5. `unrelated` (Label 0): Unrelated computational tasks
- **Positive Labels (Label 1):** 120 (80%)
- **Negative Labels (Label 0):** 30 (20%)

---

## Source Program Diversity

The 30 source program groups (`P001` - `P030`) cover diverse Computer Science domain topics:
- Dynamic Programming & Recursion (Fibonacci, Factorial, Exponentiation)
- Sorting Algorithms (Bubble Sort, Insertion Sort, Selection Sort, Merge)
- Searching Algorithms (Binary Search, Linear Search First/Last)
- Number Theory (Prime Checker, GCD/LCM)
- String Processing & Cipher (Reversal, Palindrome, Caesar Cipher, Vowel Counter, Anagrams)
- Data Structures & OOP (Stack, Queue FIFO Buffer, Binary Tree Node Counter)
- Array Aggregation & Matrices (Find Max, Sum/Average, Matrix Transpose, Remove Duplicates)
- Compression & Parsing (Run-Length Encoding, Valid Parentheses Checker, Pascal's Triangle)

---

## Data Leakage Prevention & Cross-Validation Protocol

To prevent evaluation contamination, individual pairs derived from the same underlying source program (`P001` .. `P030`) **are never split across training and testing sets**.

- **Grouping Key:** `source_program_id` (6 source program groups per fold)
- **Folds:** 5 folds x 30 pairs = 150 pairs total.
- **Stratification:** Each fold contains exactly 6 Exact, 6 Rename, 6 Struct, 6 AI Rewrite, and 6 Unrelated pairs.
- **Zero Leakage:** No source program appears in more than one fold.

---

## Licensing & Provenance

- **Provenance:** 100% internal controlled synthetic generation by the EHSA Research Team.
- **License:** MIT License. Free for research and commercial evaluation.
