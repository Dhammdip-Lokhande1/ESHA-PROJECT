"""
tests/test_transformation_detector.py
=======================================
Test suite for explain/transformation_detector.py.

Verifies:
  1. All 6 categories are reachable with appropriate scores
  2. ai_likelihood is wired into 'likely_ai_rewrite' (fixes prior gap)
  3. Return dict always has 'type', 'confidence', 'rule_matched', 'scores_snapshot'
  4. confidence is in [0.0, 1.0]
  5. type is one of the 6 valid strings
  6. Behavioral divergence with high lexical/structural → not exact_copy
  7. Null behavioral doesn't crash
  8. Null semantic doesn't crash
  9. rule_matched string references actual score values
 10. Priority: ai_rewrite check happens before exact_copy
"""
from __future__ import annotations

import pytest

from app.explain.transformation_detector import (
    AI_REWRITE_THRESHOLD,
    EXACT_COPY_LEX_MIN,
    EXACT_COPY_STRUCT_MIN,
    PARTIAL_MATCH_MIN,
    REFACTOR_STRUCT_MIN,
    RENAME_LEX_MAX,
    RENAME_STRUCT_MIN,
    detect_transformation,
)

VALID_TYPES = {
    "exact_copy",
    "variable_renaming",
    "structural_refactoring",
    "likely_ai_rewrite",
    "partial_match",
    "unrelated",
}


def _assert_result_structure(result: dict) -> None:
    """Assert all required keys are present."""
    assert "type" in result, "Missing 'type'"
    assert "confidence" in result, "Missing 'confidence'"
    assert "rule_matched" in result, "Missing 'rule_matched'"
    assert "scores_snapshot" in result, "Missing 'scores_snapshot'"
    assert result["type"] in VALID_TYPES, f"Unknown type: {result['type']}"
    assert 0.0 <= result["confidence"] <= 1.0, f"confidence out of range: {result['confidence']}"
    assert isinstance(result["rule_matched"], str) and len(result["rule_matched"]) > 0


class TestDetectTransformationStructure:
    """All results must have the correct structure."""

    def test_result_has_required_keys(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": 0.5,
                  "behavioral": None, "fusion": 0.5}
        result = detect_transformation(scores, ai_likelihood=0.0)
        _assert_result_structure(result)

    def test_confidence_in_range(self):
        for s in [0.0, 0.3, 0.6, 0.9, 1.0]:
            scores = {"lexical": s, "structural": s, "semantic": s,
                      "behavioral": None, "fusion": s}
            result = detect_transformation(scores, ai_likelihood=0.0)
            assert 0.0 <= result["confidence"] <= 1.0

    def test_type_always_valid(self):
        test_cases = [
            {"lexical": 1.0, "structural": 1.0, "semantic": 1.0, "behavioral": None, "fusion": 1.0},
            {"lexical": 0.0, "structural": 0.0, "semantic": 0.0, "behavioral": None, "fusion": 0.0},
            {"lexical": 0.5, "structural": 0.95, "semantic": 0.5, "behavioral": None, "fusion": 0.6},
            {"lexical": None, "structural": None, "semantic": None, "behavioral": None, "fusion": None},
        ]
        for scores in test_cases:
            result = detect_transformation(scores, ai_likelihood=0.0)
            assert result["type"] in VALID_TYPES


class TestExactCopy:
    def test_exact_copy_detected(self):
        scores = {
            "lexical": EXACT_COPY_LEX_MIN + 0.05,
            "structural": EXACT_COPY_STRUCT_MIN + 0.05,
            "semantic": 0.95,
            "behavioral": None,
            "fusion": 0.95,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "exact_copy", f"Expected exact_copy, got {result['type']}"

    def test_exact_copy_high_confidence(self):
        scores = {
            "lexical": 1.0, "structural": 1.0,
            "semantic": 1.0, "behavioral": None, "fusion": 1.0,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "exact_copy"
        assert result["confidence"] > 0.5

    def test_exact_copy_with_behavioral_divergence_not_exact_copy(self):
        """If behavioral is very low but lexical+structural are very high,
        outputs diverge despite textual similarity — should not be exact_copy."""
        from app.explain.transformation_detector import BEHAVIORAL_DIVERGE_MAX
        scores = {
            "lexical": 0.98, "structural": 0.98,
            "semantic": 0.95, "behavioral": BEHAVIORAL_DIVERGE_MAX - 0.05, "fusion": 0.75,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        # Should fall through to a different category
        assert result["type"] != "exact_copy", \
            "Behavioral divergence should prevent exact_copy classification"


class TestVariableRenaming:
    def test_rename_detected(self):
        scores = {
            "lexical": RENAME_LEX_MAX - 0.1,        # below threshold → different identifiers
            "structural": RENAME_STRUCT_MIN + 0.05,  # above → same structure
            "semantic": 0.85,
            "behavioral": None,
            "fusion": 0.7,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "variable_renaming", \
            f"Expected variable_renaming, got {result['type']} (scores={scores})"

    def test_rename_rule_matched_references_scores(self):
        scores = {
            "lexical": 0.50, "structural": 0.95,
            "semantic": 0.85, "behavioral": None, "fusion": 0.75,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        if result["type"] == "variable_renaming":
            # rule_matched must reference actual numbers
            assert "0.95" in result["rule_matched"] or "0.50" in result["rule_matched"], \
                "rule_matched must reference actual score values"


class TestStructuralRefactoring:
    def test_refactoring_detected_with_semantic(self):
        scores = {
            "lexical": 0.4,
            "structural": (REFACTOR_STRUCT_MIN + REFACTOR_STRUCT_MIN + 0.2) / 2,  # mid-range
            "semantic": 0.75,  # high — same intent
            "behavioral": None,
            "fusion": 0.6,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "structural_refactoring", \
            f"Expected structural_refactoring, got {result['type']}"

    def test_refactoring_detected_with_lexical(self):
        scores = {
            "lexical": 0.5,    # above REFACTOR_LEX_MIN
            "structural": 0.70,  # in refactor range
            "semantic": 0.4,   # below semantic threshold — uses lexical instead
            "behavioral": None,
            "fusion": 0.55,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] in ("structural_refactoring", "partial_match"), \
            f"Unexpected type: {result['type']}"


class TestLikelyAiRewrite:
    def test_ai_rewrite_detected_at_threshold(self):
        scores = {
            "lexical": 0.5, "structural": 0.5, "semantic": 0.5,
            "behavioral": None, "fusion": 0.5,
        }
        result = detect_transformation(scores, ai_likelihood=AI_REWRITE_THRESHOLD + 0.05)
        assert result["type"] == "likely_ai_rewrite", \
            f"Expected likely_ai_rewrite, got {result['type']}"

    def test_ai_rewrite_takes_priority_over_exact_copy(self):
        """AI rewrite check MUST happen before exact_copy. This was the prior build's gap."""
        scores = {
            "lexical": 1.0, "structural": 1.0, "semantic": 1.0,
            "behavioral": None, "fusion": 1.0,
        }
        # Even with perfect similarity, high ai_likelihood → likely_ai_rewrite
        result = detect_transformation(scores, ai_likelihood=0.90)
        assert result["type"] == "likely_ai_rewrite", (
            "AI rewrite check must take priority over exact_copy. "
            "This was the known prior-build gap where ai_likelihood was siloed."
        )

    def test_ai_rewrite_below_threshold_not_triggered(self):
        scores = {
            "lexical": 0.5, "structural": 0.5, "semantic": 0.5,
            "behavioral": None, "fusion": 0.5,
        }
        result = detect_transformation(scores, ai_likelihood=AI_REWRITE_THRESHOLD - 0.10)
        assert result["type"] != "likely_ai_rewrite"

    def test_ai_rewrite_confidence_grows_with_likelihood(self):
        scores = {
            "lexical": 0.5, "structural": 0.5, "semantic": 0.5,
            "behavioral": None, "fusion": 0.5,
        }
        r1 = detect_transformation(scores, ai_likelihood=AI_REWRITE_THRESHOLD + 0.01)
        r2 = detect_transformation(scores, ai_likelihood=0.95)
        if r1["type"] == "likely_ai_rewrite" and r2["type"] == "likely_ai_rewrite":
            assert r2["confidence"] >= r1["confidence"], \
                "Higher ai_likelihood should yield higher confidence"

    def test_ai_rewrite_rule_matched_mentions_ai(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": 0.5,
                  "behavioral": None, "fusion": 0.5}
        result = detect_transformation(scores, ai_likelihood=0.80)
        assert result["type"] == "likely_ai_rewrite"
        rule = result["rule_matched"].lower()
        assert "ai" in rule or "generation" in rule or "likelihood" in rule


class TestPartialMatch:
    def test_partial_match_detected(self):
        scores = {
            "lexical": PARTIAL_MATCH_MIN + 0.05,
            "structural": PARTIAL_MATCH_MIN + 0.05,
            "semantic": 0.4,
            "behavioral": None,
            "fusion": PARTIAL_MATCH_MIN + 0.05,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] in ("partial_match", "structural_refactoring"), \
            f"Unexpected type: {result['type']}"

    def test_partial_match_not_unrelated(self):
        scores = {
            "lexical": 0.35, "structural": 0.35,
            "semantic": 0.35, "behavioral": None, "fusion": 0.35,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] != "unrelated"


class TestUnrelated:
    def test_unrelated_detected(self):
        scores = {
            "lexical": 0.05, "structural": 0.05, "semantic": 0.05,
            "behavioral": None, "fusion": 0.05,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "unrelated"

    def test_all_zeros_unrelated(self):
        scores = {
            "lexical": 0.0, "structural": 0.0, "semantic": 0.0,
            "behavioral": 0.0, "fusion": 0.0,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "unrelated"

    def test_low_fusion_score_classified_as_unrelated_even_if_component_exceeds_threshold(self):
        """Regression test for P-03 / FIX 3:
        If fusion_score is 0.28 (< 0.30), but semantic cosine is 0.31 (>= 0.30),
        the pair MUST be classified as 'unrelated' because fusion_score is below
        the PARTIAL_MATCH_MIN noise floor threshold.
        """
        scores = {
            "lexical": 0.10,
            "structural": 0.10,
            "semantic": 0.31,
            "behavioral": 0.10,
            "fusion": 0.28,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] == "unrelated", (
            f"Expected 'unrelated' for fusion=0.28, got '{result['type']}'"
        )



class TestEdgeCases:
    def test_all_none_scores(self):
        scores = {
            "lexical": None, "structural": None, "semantic": None,
            "behavioral": None, "fusion": None,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        _assert_result_structure(result)
        assert result["type"] == "unrelated"

    def test_behavioral_none_doesnt_crash(self):
        scores = {
            "lexical": 0.9, "structural": 0.95, "semantic": 0.8,
            "behavioral": None, "fusion": 0.88,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        _assert_result_structure(result)

    def test_scores_snapshot_always_present(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": 0.5,
                  "behavioral": 0.5, "fusion": 0.5}
        result = detect_transformation(scores, ai_likelihood=0.3)
        assert "ai_likelihood" in result["scores_snapshot"]
        assert result["scores_snapshot"]["ai_likelihood"] == 0.3

    def test_ai_likelihood_zero_never_triggers_ai_rewrite(self):
        scores = {
            "lexical": 0.5, "structural": 0.5, "semantic": 0.5,
            "behavioral": None, "fusion": 0.5,
        }
        result = detect_transformation(scores, ai_likelihood=0.0)
        assert result["type"] != "likely_ai_rewrite"
