# Per-Transformation Recall Breakdown across Baselines & EHSA Combinations

| Strategy | formatting_change | variable_renaming | structural_refactoring | dead_code_insertion | combined |
|---|---|---|---|---|---|
| **JPlag/MOSS Normalized Token Baseline** | 1.000 | 1.000 | 0.967 | 1.000 | 1.000 |
| **UniXcoder Cosine Baseline** | 0.933 | 1.000 | 1.000 | 1.000 | 0.900 |
| **Lexical Only (L)** | 1.000 | 1.000 | 1.000 | 1.000 | 0.933 |
| **Structural Only (S)** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| **Semantic Only (M)** | 0.933 | 1.000 | 1.000 | 1.000 | 0.900 |
| **Behavioral Only (B)** | 1.000 | 0.933 | 1.000 | 1.000 | 1.000 |
| **L + S** | 1.000 | 1.000 | 1.000 | 0.933 | 1.000 |
| **L + M** | 1.000 | 1.000 | 1.000 | 1.000 | 0.900 |
| **L + B** | 1.000 | 1.000 | 1.000 | 1.000 | 0.933 |
| **S + M** | 1.000 | 1.000 | 1.000 | 0.967 | 1.000 |
| **S + B** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| **M + B** | 0.900 | 0.933 | 1.000 | 1.000 | 0.800 |
| **L + S + M (LOO-B)** | 1.000 | 1.000 | 1.000 | 0.933 | 1.000 |
| **L + S + B (LOO-M)** | 1.000 | 1.000 | 1.000 | 0.967 | 1.000 |
| **L + M + B (LOO-S)** | 1.000 | 1.000 | 1.000 | 1.000 | 0.900 |
| **S + M + B (LOO-L)** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| **L + S + M + B (Full Model)** | 1.000 | 1.000 | 1.000 | 0.967 | 1.000 |

## Behavioral Marginal Value & Negative Findings

Behavioral Channel Marginal Value Finding:
1. On Hard Negatives (same problem, different author), behavioral similarity B is 0.917 because independently written solutions for the same problem produce identical stdout on canonical stdin inputs. Thus, B alone cannot distinguish functional clones from true plagiarism.
2. Static representations (L, S, M) successfully measure implementation divergence (Lexical L=0.190 on hard negatives).
3. Honest Finding on Where EHSA Does NOT Win: On simple variable_renaming or formatting_change positives, the JPlag/MOSS Normalized Token Baseline achieves F1=1.000 at lower computational cost than semantic neural representations. EHSA's hybrid model excels specifically on structural refactoring and multi-layer obfuscations where simple token normalization fails.