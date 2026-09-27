"""
tests/test_fusion.py
=====================
Test suite for fusion/fusion_engine.py.

Verifies:
  1. Fixed weights produce correct weighted average
  2. Null behavioral is excluded (not zeroed) and weights renormalized
  3. Null semantic is handled
  4. All signals null → (0.0, metadata with note)
  5. weight_metadata always present (Non-Negotiable Rule 5)
  6. weight_metadata has required keys: effective_weights, source, signals_used
  7. Explicit weights override config defaults
  8. Equal-weight fallback when base weights have no coverage for available signals
  9. Score is in [0.0, 1.0]
 10. Symmetry of fusion (same inputs → same output)
"""
from __future__ import annotations

import pytest

from app.fusion.fusion_engine import fuse


def _assert_weight_metadata(metadata: dict) -> None:
    """Assert that weight_metadata has all required keys (Non-Negotiable Rule 5)."""
    required_keys = [
        "effective_weights",
        "behavioral_excluded",
        "excluded_signals",
        "signals_used",
        "source",
        "last_updated",
    ]
    for key in required_keys:
        assert key in metadata, f"weight_metadata missing required key: '{key}'"


class TestFuse:
    def test_all_signals_present_fixed_weights(self):
        scores = {
            "lexical": 0.8,
            "structural": 0.9,
            "semantic": 0.7,
            "behavioral": 0.6,
        }
        weights = {
            "lexical": 0.25,
            "structural": 0.25,
            "semantic": 0.25,
            "behavioral": 0.25,
        }
        score, metadata = fuse(scores, weights=weights)
        expected = 0.25 * 0.8 + 0.25 * 0.9 + 0.25 * 0.7 + 0.25 * 0.6
        assert score == pytest.approx(expected, abs=1e-5)
        _assert_weight_metadata(metadata)

    def test_null_behavioral_excluded_not_zeroed(self):
        """None behavioral must be excluded from fusion, not treated as 0.0."""
        scores_with = {
            "lexical": 0.8,
            "structural": 0.9,
            "semantic": 0.7,
            "behavioral": 0.5,  # present
        }
        scores_without = {
            "lexical": 0.8,
            "structural": 0.9,
            "semantic": 0.7,
            "behavioral": None,  # absent
        }
        weights = {
            "lexical": 0.25,
            "structural": 0.25,
            "semantic": 0.25,
            "behavioral": 0.25,
        }
        score_with, _ = fuse(scores_with, weights=weights)
        score_without, metadata = fuse(scores_without, weights=weights)

        # Without behavioral, remaining signals are renormalized to 1/3 each
        expected_without = (0.8 + 0.9 + 0.7) / 3.0
        assert score_without == pytest.approx(expected_without, abs=1e-5)
        assert metadata["behavioral_excluded"] is True
        assert "behavioral" in metadata["excluded_signals"]

    def test_null_behavioral_does_not_equal_zero_behavioral(self):
        """Explicitly verify None ≠ 0.0 behavioral produces different scores."""
        w = {"lexical": 0.25, "structural": 0.25, "semantic": 0.25, "behavioral": 0.25}
        score_none, _ = fuse(
            {"lexical": 0.8, "structural": 0.9, "semantic": 0.7, "behavioral": None},
            weights=w,
        )
        score_zero, _ = fuse(
            {"lexical": 0.8, "structural": 0.9, "semantic": 0.7, "behavioral": 0.0},
            weights=w,
        )
        # None excludes behavioral (score ≈ 0.8), 0.0 behavioral drags score down
        assert score_none != pytest.approx(score_zero, abs=0.01), (
            "None behavioral must produce a different score than 0.0 behavioral — "
            "they have different meanings."
        )

    def test_null_semantic_excluded(self):
        scores = {
            "lexical": 0.6,
            "structural": 0.8,
            "semantic": None,
            "behavioral": None,
        }
        weights = {"lexical": 0.25, "structural": 0.25, "semantic": 0.35, "behavioral": 0.15}
        score, metadata = fuse(scores, weights=weights)
        expected = (0.25 * 0.6 + 0.25 * 0.8) / (0.25 + 0.25)
        assert score == pytest.approx(expected, abs=1e-5)
        assert "semantic" in metadata["excluded_signals"]
        _assert_weight_metadata(metadata)

    def test_all_null_returns_zero(self):
        scores = {"lexical": None, "structural": None, "semantic": None, "behavioral": None}
        score, metadata = fuse(scores, weights=None)
        assert score == 0.0
        assert metadata["signals_used"] == []
        _assert_weight_metadata(metadata)

    def test_weight_metadata_always_present(self):
        """Non-Negotiable Rule 5: weight_metadata must always be returned."""
        for s in [
            {"lexical": 0.5, "structural": 0.5, "semantic": 0.5, "behavioral": 0.5},
            {"lexical": 0.5, "structural": 0.5, "semantic": None, "behavioral": None},
            {"lexical": None, "structural": None, "semantic": None, "behavioral": None},
        ]:
            _, metadata = fuse(s, weights=None)
            assert isinstance(metadata, dict)
            _assert_weight_metadata(metadata)

    def test_effective_weights_sum_to_one(self):
        """Effective (normalized) weights must sum to ~1.0."""
        scores = {"lexical": 0.7, "structural": 0.8, "semantic": 0.6, "behavioral": None}
        _, metadata = fuse(scores, weights=None)
        total = sum(metadata["effective_weights"].values())
        assert total == pytest.approx(1.0, abs=1e-6)

    def test_score_in_valid_range(self):
        for scores in [
            {"lexical": 1.0, "structural": 1.0, "semantic": 1.0, "behavioral": 1.0},
            {"lexical": 0.0, "structural": 0.0, "semantic": 0.0, "behavioral": 0.0},
            {"lexical": 0.5, "structural": 0.5, "semantic": None, "behavioral": None},
            {"lexical": None, "structural": None, "semantic": None, "behavioral": None},
        ]:
            score, _ = fuse(scores, weights=None)
            assert 0.0 <= score <= 1.0, f"Score out of range: {score} for {scores}"

    def test_explicit_weights_override_config(self):
        scores = {"lexical": 1.0, "structural": 0.0, "semantic": 0.0, "behavioral": None}
        weights_lex_heavy = {"lexical": 0.9, "structural": 0.05, "semantic": 0.05, "behavioral": 0.0}
        weights_struct_heavy = {"lexical": 0.05, "structural": 0.9, "semantic": 0.05, "behavioral": 0.0}
        score_lex, meta_lex = fuse(scores, weights=weights_lex_heavy)
        score_struct, meta_struct = fuse(scores, weights=weights_struct_heavy)
        assert score_lex > score_struct, "Lexical-heavy weights should give higher score when lexical=1.0"
        assert meta_lex["source"] == "explicit"

    def test_source_is_config_default_when_no_db(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": 0.5, "behavioral": 0.5}
        _, metadata = fuse(scores, weights=None, db_session=None)
        assert metadata["source"] == "config_default"

    def test_signals_used_matches_non_null(self):
        scores = {"lexical": 0.5, "structural": 0.5, "semantic": None, "behavioral": None}
        _, metadata = fuse(scores, weights=None)
        assert set(metadata["signals_used"]) == {"lexical", "structural"}

    def test_identical_scores_pure_average(self):
        """When all scores equal x, fused score should equal x."""
        for x in [0.0, 0.5, 1.0]:
            scores = {"lexical": x, "structural": x, "semantic": x, "behavioral": x}
            score, _ = fuse(scores, weights=None)
            assert score == pytest.approx(x, abs=1e-6)

    def test_only_one_signal_available(self):
        """With only one signal available, score equals that signal's value."""
        scores = {"lexical": 0.75, "structural": None, "semantic": None, "behavioral": None}
        score, metadata = fuse(scores, weights=None)
        assert score == pytest.approx(0.75, abs=1e-6)
        assert metadata["effective_weights"]["lexical"] == pytest.approx(1.0, abs=1e-6)

    def test_equal_weight_fallback(self):
        """If base_weights have 0 coverage for available signals, use equal weights."""
        scores = {"lexical": 0.6, "structural": 0.8, "semantic": None, "behavioral": None}
        # Weights that only assign weight to semantic and behavioral (both absent)
        weird_weights = {"lexical": 0.0, "structural": 0.0, "semantic": 0.5, "behavioral": 0.5}
        score, metadata = fuse(scores, weights=weird_weights)
        # Should fall back to equal weights for lexical+structural → (0.6+0.8)/2 = 0.7
        assert score == pytest.approx(0.7, abs=1e-5)
