# Dataset Card for EHSA Research Benchmark (v1.0)

## Dataset Description

The EHSA Research Benchmark is a dataset of 150 unique, functionally validated Python code pairs created for evaluating multi-view explainable source-code similarity detection engines.

- **Curated By:** EHSA Research Team
- **Language:** Python 3
- **Pairs:** 150
- **Source Groups:** 30
- **License:** MIT

---

## Intended Use

### Primary Intended Uses
- Evaluating multi-signal code similarity analyzers across lexical, structural, semantic, and behavioral dimensions.
- Measuring model robustly against specific code transformation techniques (renaming, structural refactoring, AI rewrites).

### Out-of-Scope Uses
- This dataset is not intended to represent the full spectrum of real-world academic dishonesty or large-scale multi-file repository plagiarism.

---

## Dataset Composition & Summary

| Category | Pair Count | Label | Description |
|---|---|---|---|
| **Exact Copy** | 30 | 1 | Identical code with comment and whitespace variations |
| **Variable Renaming** | 30 | 1 | Systematic renaming of variables and parameters |
| **Structural Refactoring** | 30 | 1 | Loop conversions, recursion to iteration, list comprehensions |
| **AI Rewrite** | 30 | 1 | Pythonic idiomatic rewrites using stdlib (`math`, `itertools`, `collections`) |
| **Unrelated** | 30 | 0 | Pairs implementing completely different algorithms |

---

## Quality Control & Functional Validation

Each behavior-preserving positive pair was subjected to automated functional execution testing:
- **Test Harness:** Both `code_a` and `code_b` were executed with identical test input arguments in an isolated sandbox.
- **Assertion:** Execution verified output equivalence (`res_a == res_b`).
- **Validation Status:** Recorded in `metadata.json` (`validation_status: "passed"`).

---

## Leakage Prevention Protocol

Data leakage is prevented by grouping pairs strictly by `source_program_id`. 
All 5 transformation variants derived from a single base program (e.g., `P001`) belong exclusively to one cross-validation fold. Unseen test folds never contain variants of base programs present in training folds.

---

## Ethical & Provenance Considerations

- All code pairs in this benchmark were synthetically generated in a controlled environment.
- No public user code, private student submissions, or external copyrighted repositories were included without authorization.
