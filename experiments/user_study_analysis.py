"""
experiments/user_study_analysis.py
==================================
Statistical analysis script for M10 Instructor User Study.

NOTE / SCRIPT VALIDATION NOTICE:
This script computes descriptive statistics and the Wilcoxon signed-rank test.
When run against synthetic pilot data (user_study_data_SYNTHETIC_PILOT.csv),
it serves ONLY as a script validation check to confirm the statistical pipeline logic.
It MUST NOT be reported as a completed human instructor study.
When real human participant responses are collected in user_study_data.csv, this script
will output the citable publication results for M10 / RQ3.
"""

import os
import csv
from scipy.stats import wilcoxon

def analyze():
    # Prefer real human participant dataset if present, fallback to synthetic pilot file for script validation
    real_data_file = os.path.join(os.path.dirname(__file__), "user_study_data.csv")
    pilot_data_file = os.path.join(os.path.dirname(__file__), "user_study_data_SYNTHETIC_PILOT.csv")

    if os.path.exists(real_data_file):
        data_file = real_data_file
        is_synthetic = False
        print(f"Loading REAL human instructor data from: {data_file}")
    elif os.path.exists(pilot_data_file):
        data_file = pilot_data_file
        is_synthetic = True
        print(f"Loading SYNTHETIC PILOT data for SCRIPT VALIDATION from: {data_file}")
    else:
        print(f"No user study data file found at {real_data_file} or {pilot_data_file}.")
        return

    scores = {}
    with open(data_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['participant_id']}_{row['pair_id']}"
            if key not in scores:
                scores[key] = {}
            if row.get('confidence_score'):
                scores[key][row['condition']] = int(row['confidence_score'])

    score_only = []
    explainable = []

    for key, condition_scores in scores.items():
        if "score_only" in condition_scores and "explainable" in condition_scores:
            score_only.append(condition_scores["score_only"])
            explainable.append(condition_scores["explainable"])

    if not score_only:
        print("No valid paired data found.")
        return

    mean_score_only = sum(score_only) / len(score_only)
    mean_explainable = sum(explainable) / len(explainable)

    print(f"Mean Confidence (Score Only): {mean_score_only:.2f}")
    print(f"Mean Confidence (Explainable): {mean_explainable:.2f}")

    stat, p_value = wilcoxon(score_only, explainable, zero_method='wilcox', correction=False)

    print(f"Wilcoxon Statistic: {stat}")
    print(f"P-Value: {p_value:.4e}")

    report_file = os.path.join(os.path.dirname(__file__), "user_study_results.md")
    with open(report_file, "w") as f:
        f.write("# M10: Instructor User Study Analysis\n\n")

        if is_synthetic:
            f.write("> **SCRIPT VALIDATION NOTICE:** This output was generated using **synthetic pilot data (seed=42)** to validate the analysis script pipeline. **Real human participant collection is pending.**\n\n")

        f.write("## Overview\n")
        f.write(f"Analyzed {len(score_only)} paired evaluations across **Score-Only** (Control) and **Explainable** (Treatment) conditions.\n\n")

        f.write("## Descriptive Statistics\n")
        f.write(f"- **Mean Confidence (Score-Only)**: {mean_score_only:.2f}\n")
        f.write(f"- **Mean Confidence (Explainable)**: {mean_explainable:.2f}\n\n")

        f.write("## Wilcoxon Signed-Rank Test\n")
        f.write(f"The Wilcoxon signed-rank test yielded a p-value of **{p_value:.4e}** (Statistic: {stat}).\n\n")

        f.write("## Conclusion\n")
        if p_value < 0.05:
            f.write(f"Since the p-value ({p_value:.4e}) < 0.05, there is a **statistically significant improvement** in instructor confidence when provided with full explainable evidence.\n")
        else:
            f.write(f"Difference is not statistically significant (p = {p_value:.4e}).\n")

    print("Report written to user_study_results.md")

if __name__ == "__main__":
    analyze()
