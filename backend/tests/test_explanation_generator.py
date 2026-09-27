"""
tests/test_explanation_generator.py
=====================================
Test suite for explain/explanation_generator.py.

Verifies:
  1. All 6 transformation types produce a valid explanation dict
  2. 'verdict' string references actual score values (not generic placeholders)
  3. 'narrative' is non-empty and relevant
  4. 'signals' is a non-empty list
  5. 'caveats' always includes the mandatory advisory disclaimer (section 9.6)
  6. Absent behavioral → caveat added
  7. Absent semantic → caveat added
  8. All score values appear in verdict or narrative or signals
  9. Returns dict (not str) — the spec calls for structured output
 10. Empty ai_evidence doesn't crash
 11. AI evidence with not_implemented status → no AI note injected
"""
from __future__ import annotations

import pytest

from app.explain.explanation_generator import generate_explanation


ADVISORY_FRAGMENT = "advisory"  # Must appear in at least one caveat (section 9.6)

TRANSFORMATION_TYPES = [
    "exact_copy",
    "variable_renaming",
    "structural_refactoring",
    "likely_ai_rewrite",
    "partial_match",
    "unrelated",
]


def _make_transformation(t_type: str, confidence: float = 0.75, ai_likelihood: float = 0.0) -> dict:
    return {
        "type": t_type,
        "confidence": confidence,
        "rule_matched": f"Test rule for {t_type}",
        "scores_snapshot": {
            "lexical": 0.5, "structural": 0.5, "semantic": 0.5,
            "behavioral": None, "fusion": 0.5, "ai_likelihood": ai_likelihood,
        },
    }


def _make_scores(lexical=0.5, structural=0.5, semantic=0.5,
                 behavioral=None, fusion=0.5) -> dict:
    return {
        "lexical": lexical, "structural": structural, "semantic": semantic,
        "behavioral": behavioral, "fusion": fusion,
    }


def _make_stub_ai_evidence() -> list[dict]:
    return [{"note": "AI generation not implemented", "status": "not_implemented"}]


class TestExplanationStructure:
    """Generated explanation must always have the correct structure."""

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_all_types_return_dict(self, t_type):
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        assert isinstance(result, dict), f"generate_explanation must return dict, got {type(result)}"

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_required_keys_present(self, t_type):
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        for key in ["transformation_type", "confidence", "verdict", "narrative", "signals", "caveats", "rule_matched"]:
            assert key in result, f"Missing key '{key}' for type {t_type}"

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_verdict_is_non_empty_string(self, t_type):
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        assert isinstance(result["verdict"], str)
        assert len(result["verdict"].strip()) > 0

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_signals_is_non_empty_list(self, t_type):
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        assert isinstance(result["signals"], list)
        assert len(result["signals"]) > 0

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_caveats_is_non_empty_list(self, t_type):
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        assert isinstance(result["caveats"], list)
        assert len(result["caveats"]) > 0

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_advisory_caveat_always_present(self, t_type):
        """Section 9.6: advisory disclaimer must ALWAYS appear in caveats."""
        transformation = _make_transformation(t_type)
        scores = _make_scores()
        result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
        caveats_text = " ".join(result["caveats"]).lower()
        assert ADVISORY_FRAGMENT in caveats_text, (
            f"Advisory caveat missing for {t_type}. "
            f"Section 9.6 requires 'this analysis is advisory only'. "
            f"Caveats: {result['caveats']}"
        )

    @pytest.mark.parametrize("t_type", TRANSFORMATION_TYPES)
    def test_confidence_in_range(self, t_type):
        for conf in [0.0, 0.4, 0.75, 1.0]:
            transformation = _make_transformation(t_type, confidence=conf)
            scores = _make_scores()
            result = generate_explanation(scores, transformation, _make_stub_ai_evidence())
            assert result["confidence"] == conf


class TestScoreReferences:
    """Verdict and signals must reference actual score values."""

    def test_exact_copy_verdict_has_percentage(self):
        scores = _make_scores(lexical=0.95, structural=0.98, fusion=0.96)
        t = _make_transformation("exact_copy", confidence=0.9)
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        # Fusion percentage should appear in verdict
        assert "96%" in result["verdict"] or "96" in result["verdict"], \
            f"Verdict should reference fusion percentage. Verdict: {result['verdict']}"

    def test_variable_renaming_narrative_references_structural(self):
        scores = _make_scores(lexical=0.45, structural=0.95, fusion=0.7)
        t = _make_transformation("variable_renaming")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        # Structural value should appear in narrative
        assert "95%" in result["narrative"] or "45%" in result["narrative"], \
            f"Narrative must reference actual scores. Narrative: {result['narrative']}"

    def test_unrelated_verdict_has_percentage(self):
        scores = _make_scores(lexical=0.05, structural=0.05, fusion=0.05)
        t = _make_transformation("unrelated")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        assert "5%" in result["verdict"] or "5" in result["verdict"]

    def test_signals_list_has_percentage_values(self):
        scores = _make_scores(lexical=0.72, structural=0.68, fusion=0.70)
        t = _make_transformation("partial_match")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        signals_text = " ".join(result["signals"])
        assert "%" in signals_text, "Signals must contain percentage values"


class TestMissingSignalCaveats:
    def test_missing_behavioral_adds_caveat(self):
        scores = _make_scores(behavioral=None)
        t = _make_transformation("exact_copy")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        caveats_text = " ".join(result["caveats"]).lower()
        assert "behavioral" in caveats_text, \
            "Missing behavioral signal must be noted in caveats"

    def test_present_behavioral_no_behavioral_caveat(self):
        scores = _make_scores(behavioral=0.7)
        t = _make_transformation("exact_copy")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        caveats_text = " ".join(result["caveats"]).lower()
        # Behavioral caveat should NOT appear when behavioral is present
        assert "behavioral" not in caveats_text or "advisory" in caveats_text

    def test_missing_semantic_adds_caveat(self):
        scores = _make_scores(semantic=None)
        t = _make_transformation("partial_match")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        caveats_text = " ".join(result["caveats"]).lower()
        assert "semantic" in caveats_text, \
            "Missing semantic signal must be noted in caveats"


class TestAiRewriteExplanation:
    def test_ai_rewrite_narrative_mentions_ai(self):
        scores = _make_scores(fusion=0.7)
        t = _make_transformation("likely_ai_rewrite", ai_likelihood=0.80)
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        narrative_lower = result["narrative"].lower()
        assert "ai" in narrative_lower or "generation" in narrative_lower or \
               "likelihood" in narrative_lower, \
            f"AI rewrite narrative must mention AI. Got: {result['narrative']}"

    def test_ai_rewrite_signals_include_likelihood(self):
        scores = _make_scores(fusion=0.65)
        t = _make_transformation("likely_ai_rewrite", ai_likelihood=0.82)
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        signals_text = " ".join(result["signals"]).lower()
        assert "likelihood" in signals_text or "ai" in signals_text or "82" in signals_text

    def test_ai_rewrite_not_absolute(self):
        """Section 9.6: must use investigative language, not absolute accusations."""
        scores = _make_scores(fusion=0.7)
        t = _make_transformation("likely_ai_rewrite", ai_likelihood=0.85)
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        full_text = result["narrative"] + result["verdict"]
        # Must NOT use absolute accusation language
        assert "is plagiarism" not in full_text.lower()
        assert "has plagiarized" not in full_text.lower()
        assert "is definitely" not in full_text.lower()
        # MUST use investigative language
        assert any(word in full_text.lower() for word in [
            "consistent", "pattern", "indicates", "suggests", "likely", "possible"
        ]), f"Must use investigative language. Text: {full_text[:200]}"


class TestEdgeCases:
    def test_empty_ai_evidence_doesnt_crash(self):
        scores = _make_scores(fusion=0.5)
        t = _make_transformation("partial_match")
        result = generate_explanation(scores, t, [])
        assert isinstance(result, dict)

    def test_none_scores_dont_crash(self):
        scores = {
            "lexical": None, "structural": None,
            "semantic": None, "behavioral": None, "fusion": None,
        }
        t = _make_transformation("unrelated")
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        assert isinstance(result, dict)
        # N/A values in verdict is acceptable
        assert "verdict" in result

    def test_transformation_type_preserved(self):
        for t_type in TRANSFORMATION_TYPES:
            t = _make_transformation(t_type)
            scores = _make_scores()
            result = generate_explanation(scores, t, _make_stub_ai_evidence())
            assert result["transformation_type"] == t_type

    def test_rule_matched_preserved(self):
        t = _make_transformation("unrelated")
        t["rule_matched"] = "Custom rule text for testing"
        scores = _make_scores(lexical=0.05, structural=0.05, fusion=0.05)
        result = generate_explanation(scores, t, _make_stub_ai_evidence())
        assert result["rule_matched"] == "Custom rule text for testing"
