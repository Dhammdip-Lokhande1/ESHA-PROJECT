"""
tests/test_transformation_cls.py
==================================
Unit tests for Phase 4 transformation classifier evaluation and decision tree.
"""

import pytest
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from app.explain.transformation_detector import detect_transformation, AI_REWRITE_THRESHOLD


class TestTransformationClassifierRulesAndTree:
    def test_ai_rewrite_heuristic_indicator_wiring(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": 0.5, "behavioral": None, "fusion": 0.5}
        result = detect_transformation(scores, ai_likelihood=AI_REWRITE_THRESHOLD + 0.10)
        assert result["type"] == "likely_ai_rewrite"
        assert result["confidence"] > 0.0

    def test_decision_tree_fit_and_predict_bounds(self):
        # Synthetic train features: [lexical, structural, semantic, behavioral]
        X_tr = np.array([
            [0.98, 0.98, 0.95, 1.0],  # exact_copy
            [0.30, 0.95, 0.85, 1.0],  # variable_renaming
            [0.45, 0.70, 0.75, 1.0],  # structural_refactoring
            [0.05, 0.05, 0.05, 0.0],  # unrelated
        ])
        y_tr = np.array(["exact_copy", "variable_renaming", "structural_refactoring", "unrelated"])

        clf = DecisionTreeClassifier(max_depth=4, random_state=42)
        clf.fit(X_tr, y_tr)

        # Test prediction
        pred = clf.predict([[0.99, 0.99, 0.95, 1.0]])
        assert pred[0] == "exact_copy"

    def test_rule_threshold_boundary_coverage(self):
        # Boundary 1: exact_copy threshold boundary
        scores_boundary_1 = {"lexical": 0.92, "structural": 0.92, "semantic": 0.90, "behavioral": 1.0, "fusion": 0.92}
        res_1 = detect_transformation(scores_boundary_1, ai_likelihood=0.0)
        assert res_1["type"] == "exact_copy"

        # Boundary 2: unrelated threshold boundary
        scores_boundary_2 = {"lexical": 0.05, "structural": 0.05, "semantic": 0.05, "behavioral": 0.0, "fusion": 0.05}
        res_2 = detect_transformation(scores_boundary_2, ai_likelihood=0.0)
        assert res_2["type"] == "unrelated"
