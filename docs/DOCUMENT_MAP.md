# EHSA Active Documentation Map & Single Source of Truth Register

This document serves as the authoritative map of all active documentation files within the EHSA repository. Each active document has a designated single source of truth to prevent duplicate or conflicting data.

## 1. Master System & Benchmark Evidence Files

| Document Path | Primary Purpose | Single Source of Truth |
| :--- | :--- | :--- |
| experiments/results/CANONICAL_BENCHMARK_TABLE.md | **Master Canonical Benchmark Table** | experiments/results/REGENERATED_BENCHMARK_RESULTS.json |
| docs/COMPLETE_RESEARCH_EVIDENCE.md | Comprehensive research evidence base | CANONICAL_BENCHMARK_TABLE.md & readiness audit |
| docs/PAPER_DRAFT.md | Research paper draft | CANONICAL_BENCHMARK_TABLE.md & McNemar significance tests |
| docs/CONSTRUCT_DEFINITION.md | Research construct definition & taxonomy | Section 8 of INSTRUCTIONS.md |
| THESIS_MASTER_INFORMATION.md | Comprehensive B.Tech thesis source text | docs/COMPLETE_RESEARCH_EVIDENCE.md |
| README.md | Primary repository overview & quickstart | CANONICAL_BENCHMARK_TABLE.md |

## 2. Core Technical Specifications & Operational Instructions

| Document Path | Primary Purpose | Single Source of Truth |
| :--- | :--- | :--- |
| INSTRUCTIONS.md | Project technical specification & non-negotiables | Architecture & backend codebase |
| AGENTS.md | Standing instructions & workflow rules for agent sessions | Workspace rules |
| PROJECT_BRIEF.md | Executive summary & high-level architecture overview | INSTRUCTIONS.md |
| docs/ACTUAL_ARCHITECTURE.md | Reverse-engineered implementation architecture | ackend/app/ source code |
| docs/DEPLOYMENT.md | Production & local deployment instructions | docker-compose.yml & ackend/requirements.txt |
| docs/REFERENCES.md | Academic literature citations | Academic publications cited in paper |
| docs/SYSTEM_ARCHITECTURE_AND_WORKFLOW.md | System architecture diagrams & dataflow diagrams | ackend/app/ source code |
| docs/RESEARCH_DIAGRAMS_AND_ARCHITECTURE.md | Visual diagrams for paper/thesis | docs/SYSTEM_ARCHITECTURE_AND_WORKFLOW.md |

## 3. Thesis & Literature Support Documents

| Document Path | Primary Purpose | Single Source of Truth |
| :--- | :--- | :--- |
| EHSA_LITERATURE_REVIEW.md | Background literature & baseline comparisons | docs/REFERENCES.md |
| EHSA_METHODOLOGY.md | Multi-view similarity pipeline methodology | ackend/app/similarity/ |
| EHSA_THESIS_INFORMATION_BASE.md | High-level thesis information summary | THESIS_MASTER_INFORMATION.md |
| EHSA_VIVA_PREPARATION.md | Viva defense questions & answers | docs/COMPLETE_RESEARCH_EVIDENCE.md |

## 4. Experiment-Specific Results & Dataset Cards

| Document Path | Primary Purpose | Single Source of Truth |
| :--- | :--- | :--- |
| experiments/RESEARCH_DATASET_CONSTRUCTION_REPORT.md | Dataset curation & hard negative generation report | experiments/dataset/metadata.csv |
| experiments/dataset/README.md | Benchmark dataset directory guide | experiments/dataset/metadata.csv |
| experiments/dataset/dataset_card.md | Dataset card for EHSA synthetic benchmark | experiments/dataset/metadata.csv |
| experiments/dataset/EXTERNAL_DATASETS.md | External datasets documentation (CodeNet, OJClone) | Dataset manifests |
| experiments/dataset/transbench_lite/dataset_card.md | TransBench-Lite dataset card | 	ransbench_lite/pairs.csv |
| experiments/instructor_study_guide.md | User study protocol guide | ackend/app/explain/ |
| experiments/user_study_results.md | Synthetic pilot user study statistical output | experiments/user_study_results.md |
| experiments/results/statistical_tests_report.md | Statistical significance & McNemar tests report | experiments/results/REGENERATED_BENCHMARK_RESULTS.json |
| experiments/results/baselines_ablation/ablation_table.md | 4-channel ablation study summary | CANONICAL_BENCHMARK_TABLE.md |
| experiments/results/baselines_ablation/per_transformation_recall.md | Recall breakdown across transformation types | aselines_ablation/metrics.json |
| experiments/results/adaptive_learning_curve/learning_curve_table.md | Phase 6 adaptive learning curve results | daptive_learning_curve/metrics.json |
| experiments/results/codenet_python800/controlled/evaluation_report.md | CodeNet-100 controlled evaluation summary | CANONICAL_BENCHMARK_TABLE.md |
| experiments/results/transformation_attribution/transformation_attribution_report.md | Phase 4 transformation attribution report | 	ransformation_attribution/metrics.json |
| experiments/results/transformation_cls/transformation_cls_report.md | Phase 4 transformation classifier report | 	ransformation_cls/metrics.json |
| experiments/results/transformation_cls/misclassifications.md | Classifier error analysis report | 	ransformation_cls/misclassifications.json |
| experiments/results/transformation_cls/tree_rules.txt | DecisionTree classification rules dump | Decision tree model dump |
| docs/PHASE3A_PROTOCOL.md | Phase 3A evaluation protocol documentation | experiments/evaluate_fair.py |

---
*Note: Editing numerical results in any document listed above must strictly follow CANONICAL_BENCHMARK_TABLE.md.*
