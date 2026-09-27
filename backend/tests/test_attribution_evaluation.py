"""
tests/test_attribution_evaluation.py
======================================
Unit tests for Phase 4 transformation attribution evaluation & evidence calibration.
"""

import pytest
import numpy as np
from experiments.evaluate_transformation_attribution import compute_expected_calibration_error
from app.explain.transformation_detector import detect_transformation
from app.explain.explanation_generator import generate_explanation


class TestAttributionECE:
    def test_perfect_calibration_ece_zero(self):
        confidences = np.array([0.9, 0.9, 0.5, 0.5])
        accuracies = np.array([0.9, 0.9, 0.5, 0.5])
        ece, bin_details = compute_expected_calibration_error(confidences, accuracies, n_bins=5)
        assert ece == 0.0, f"Expected 0.0 ECE, got {ece}"

    def test_bin_details_structure(self):
        confidences = np.array([0.85, 0.75, 0.65, 0.25])
        accuracies = np.array([1.0, 1.0, 0.0, 0.0])
        ece, bin_details = compute_expected_calibration_error(confidences, accuracies, n_bins=5)
        assert len(bin_details) == 5
        assert "bin" in bin_details[0]
        assert "avg_confidence" in bin_details[0]
        assert "avg_accuracy" in bin_details[0]


class TestEvidenceCompleteness:
    def test_explanation_contains_required_evidence_fields(self):
        scores = {
            "lexical": 0.50,
            "structural": 0.92,
            "semantic": 0.85,
            "behavioral": 1.0,
            "fusion": 0.78,
        }
        det_res = detect_transformation(scores, ai_likelihood=0.0)
        exp_res = generate_explanation(scores, det_res, ai_evidence=[])

        assert exp_res["verdict"] is not None and len(exp_res["verdict"]) > 0
        assert exp_res["narrative"] is not None and len(exp_res["narrative"]) > 0
        assert len(exp_res["signals"]) >= 2
        assert len(exp_res["caveats"]) >= 1
        assert "advisory" in exp_res["caveats"][-1].lower() or "human review" in exp_res["caveats"][-1].lower()
