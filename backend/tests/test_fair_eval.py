"""
backend/tests/test_fair_eval.py
============================================================
Unit tests for Statistically Fair Evaluation & Bootstrap CIs.
"""

import unittest
import numpy as np
from experiments.evaluate_fair import (
    select_best_threshold,
    compute_metrics,
    bootstrap_pair_ci,
    compute_map_at_r_matrix,
)


class TestFairEvaluation(unittest.TestCase):
    def test_threshold_selection_no_test_leakage(self):
        """Test threshold selection maximizes F1 on train set only."""
        y_train = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        scores_train = np.array([0.9, 0.85, 0.75, 0.65, 0.45, 0.35, 0.25, 0.15])

        # Select threshold on train set
        tau, best_f1 = select_best_threshold(y_train, scores_train)
        self.assertGreaterEqual(tau, 0.45)
        self.assertLessEqual(tau, 0.65)
        self.assertEqual(best_f1, 1.0)

        # Apply tau unchanged to test set
        y_test = np.array([1, 1, 0, 0])
        scores_test = np.array([0.8, 0.7, 0.3, 0.2])
        m_test = compute_metrics(y_test, scores_test, tau)
        self.assertEqual(m_test["f1_score"], 1.0)

    def test_map_at_r_calculation(self):
        """Test MAP@R code-to-code retrieval metric calculation."""
        test_corpus = [
            {"id": "p1_a", "problem_id": 1},
            {"id": "p1_b", "problem_id": 1},
            {"id": "p2_a", "problem_id": 2},
            {"id": "p2_b", "problem_id": 2},
        ]
        # Perfect similarity matrix
        sim_mat = np.array([
            [1.0, 0.9, 0.1, 0.1],
            [0.9, 1.0, 0.1, 0.1],
            [0.1, 0.1, 1.0, 0.9],
            [0.1, 0.1, 0.9, 1.0],
        ])
        mats = {"Model": sim_mat}
        res = compute_map_at_r_matrix(test_corpus, mats)
        self.assertIn("Model", res)
        self.assertEqual(res["Model"], 1.0)

    def test_bootstrap_pair_ci(self):
        """Test 95% pair-level bootstrap confidence intervals."""
        y_true = np.array([1, 1, 1, 0, 0, 0])
        scores = np.array([0.9, 0.8, 0.7, 0.3, 0.2, 0.1])
        ci = bootstrap_pair_ci(y_true, scores, threshold=0.5, n_bootstraps=100, seed=42)

        self.assertIn("f1_score", ci)
        self.assertIn("roc_auc", ci)
        self.assertLessEqual(ci["f1_score"]["low"], ci["f1_score"]["high"])
        self.assertLessEqual(ci["roc_auc"]["low"], ci["roc_auc"]["high"])


if __name__ == "__main__":
    unittest.main()
