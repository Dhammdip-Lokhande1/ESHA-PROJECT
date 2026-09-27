# EHSA-TransBench-Lite Benchmark Dataset Card

## 1. Benchmark Overview
- **Purpose:** Plagiarism-realistic benchmark for source code similarity analysis and transformation attribution.
- **Source Data:** IBM Project CodeNet Python 3 Benchmark (Puri et al., NeurIPS 2021).
- **Total Pairs:** 420
- **Train Pairs:** 210 (150 Positive / 60 Negative)
- **Unseen Test Pairs:** 210 (150 Positive / 60 Negative)

## 2. Leakage Prevention & Split Disjointness
- **Train Problem IDs (30):** `[1, 3, 4, 5, 10, 11, 12, 13, 14, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40]`
- **Test Problem IDs (10):** `[2, 6, 7, 8, 9, 15, 16, 18, 28, 39]`
- **Disjointness Assertion:** `assert set(train_pids).isdisjoint(set(test_pids))` PASSED.

## 3. Transformation Label Counts

| Transformation Label | Count | Description |
|---|---|---|
| `none` | 120 | Untransformed negative pairs (easy / hard) |
| `formatting_change` | 60 | Whitespace, comment, and docstring modifications |
| `variable_renaming` | 60 | Scope-aware AST local variable renaming |
| `structural_refactoring` | 60 | If/else condition negations & branch swapping |
| `dead_code_insertion` | 60 | Unused helper function and variable injection |
| `combined` | 60 | Multi-stage transformation (formatting + renaming) |

## 4. Negative Pair Breakdown

| Negative Type | Count | Description |
|---|---|---|
| `easy` | 60 | Pairs from completely different problem categories |
| `hard` | 60 | Pairs from the same problem category by different authors |
| `none` | 300 | Positive transformation pairs |