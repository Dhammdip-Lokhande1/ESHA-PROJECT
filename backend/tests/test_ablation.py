"""
backend/tests/test_ablation.py
============================================================
Unit tests for 15-Combination Ablation & Behavioral Fallback.
"""

import unittest
import numpy as np
from sklearn.linear_model import LogisticRegression
from app.fusion.fusion_engine import fuse


class TestAblationPipeline(unittest.TestCase):
    def test_logistic_regression_weights_normalized(self):
        """Test fitting LogisticRegression on train split produces normalized weights."""
        np.random.seed(42)
        X_train = np.array([
            [0.9, 0.8, 0.85, 1.0],
            [0.85, 0.82, 0.88, 1.0],
            [0.1, 0.2, 0.15, 0.0],
            [0.05, 0.15, 0.2, 0.0],
        ])
        y_train = np.array([1, 1, 0, 0])

        clf = LogisticRegression(penalty="l2", C=1.0, random_state=42)
        clf.fit(X_train, y_train)

        coefs = np.clip(clf.coef_[0], 0.0001, None)
        norm_w = coefs / coefs.sum()

        self.assertAlmostEqual(sum(norm_w), 1.0, places=5)
        self.assertEqual(len(norm_w), 4)

    def test_behavioral_missing_trace_fallback(self):
        """Test fusion engine excludes missing behavioral signal and renormalizes weights."""
        scores = {
            "lexical": 0.8,
            "structural": 0.7,
            "semantic": 0.9,
            "behavioral": None,
        }
        weights = {
            "lexical": 0.25,
            "structural": 0.35,
            "semantic": 0.40,
            "behavioral": 0.00,
        }
        fused_score, meta = fuse(scores, weights=weights)

        self.assertIn("behavioral", meta["excluded_signals"])
        self.assertTrue(meta["behavioral_excluded"])
        self.assertAlmostEqual(sum(meta["effective_weights"].values()), 1.0, places=5)
        self.assertGreater(fused_score, 0.7)


if __name__ == "__main__":
    unittest.main()
