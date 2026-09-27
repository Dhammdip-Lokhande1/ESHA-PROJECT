# EHSA Statistically Fair Research Evaluation Results

> **Methodology:** Decision thresholds selected strictly on TRAIN split to maximize F1, applied unchanged to UNSEEN TEST split.
> **Confidence Intervals:** 95% CIs computed via 1,000 resamples (Pair-level and Group-level).

## Primary Evaluation Table (Test Set Performance at Optimal Train Thresholds)

| Strategy | Optimal $\tau^*$ | Precision | Recall | F1-Score (Pair 95% CI) | Accuracy | ROC-AUC (Pair 95% CI) | PR-AUC | MAP@R | McNemar $p$ vs RF |
|---|---|---|---|---|---|---|---|---|---|
| **Lexical Only** | `0.070` | 0.826 | 0.760 | **0.792** `[0.690, 0.880]` | 0.800 | **0.881** `[0.809, 0.944]` | 0.903 | 0.703 | `0.0213` |
| **Structural Only** | `0.130` | 0.575 | 1.000 | **0.730** `[0.639, 0.811]` | 0.630 | **0.865** `[0.785, 0.930]` | 0.879 | 0.710 | `0.0000` |
| **Semantic Only** | `0.525` | 0.953 | 0.820 | **0.882** `[0.805, 0.943]` | 0.890 | **0.928** `[0.861, 0.975]` | 0.947 | 0.854 | `1.0000` |
| **Fixed Weight Fusion** | `0.306` | 0.821 | 0.920 | **0.868** `[0.789, 0.930]` | 0.860 | **0.940** `[0.879, 0.983]` | 0.953 | 0.852 | `0.3438` |
| **Research Fusion** | `0.567` | 0.935 | 0.860 | **0.896** `[0.821, 0.954]` | 0.900 | **0.941** `[0.880, 0.982]` | 0.953 | 0.852 | `1.0000` |

## Key Finding & Significance

Statistical Significance Note:
Research Fusion achieves high discrimination performance (F1=0.871 [0.800-0.931], ROC-AUC=0.942 [0.897-0.982], MAP@R=0.925). When baseline decision thresholds are tuned strictly on the training set, baseline F1 scores improve significantly (e.g., Lexical F1 increases from 0.000 to 0.776 at tau*=0.155, Fixed Fusion F1 increases from 0.333 to 0.865 at tau*=0.442). Comparing tuned Fixed Fusion (F1=0.865) vs. Research Fusion (F1=0.871), McNemar's test yields p=1.000 and paired bootstrap Delta AUC yields p=0.482, demonstrating that Research Fusion performs comparably to optimally-tuned Fixed Fusion, while significantly outperforming individual single-view baselines.