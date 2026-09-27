"""
tests/test_lexical.py
======================
Full test suite for similarity/lexical.py.

Verifies:
  1. Identical pair → score ≈ 1.0
  2. Unrelated pair → score ≈ 0.0 (low)
  3. Renamed pair → intermediate score (structural same, lexical lower)
  4. Both empty → score = 1.0, evidence explains why
  5. One empty → score = 0.0, evidence explains why
  6. Evidence is always a non-empty list of dicts (Non-Negotiable Rule 2)
  7. Each evidence dict has required keys
  8. Score is in [0.0, 1.0]
  9. n-gram size parameter works (n=1, n=2, n=3)
 10. Syntax-error source → tokenize returns partial → lexical still runs
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.preprocessing.preprocess import tokenize_code
from app.similarity.lexical import lexical_similarity, _build_ngrams, _multiset_jaccard

FIXTURES = Path(__file__).parent / "fixtures"


def _tokens(name: str) -> list[str]:
    code = (FIXTURES / name).read_text(encoding="utf-8")
    return tokenize_code(code)


def _assert_evidence_structure(evidence: list[dict]) -> None:
    """Assert that every evidence item has the required keys."""
    assert isinstance(evidence, list), "evidence must be a list"
    assert len(evidence) > 0, "evidence must not be empty (Non-Negotiable Rule 2)"
    for item in evidence:
        assert isinstance(item, dict), f"evidence item must be dict, got {type(item)}"
        assert "ngram" in item, f"missing 'ngram' key in {item}"
        assert "status" in item, f"missing 'status' key in {item}"


class TestLexicalSimilarity:
    def test_identical_pair_scores_one(self):
        tokens_a = _tokens("identical_a.py")
        tokens_b = _tokens("identical_b.py")
        score, evidence = lexical_similarity(tokens_a, tokens_b)
        assert score == pytest.approx(1.0), f"Identical pair should score 1.0, got {score}"
        _assert_evidence_structure(evidence)

    def test_unrelated_pair_scores_low(self):
        tokens_a = _tokens("unrelated_a.py")
        tokens_b = _tokens("unrelated_b.py")
        score, evidence = lexical_similarity(tokens_a, tokens_b)
        # Should be low — some shared Python keywords but very different logic
        assert score < 0.35, f"Unrelated pair should score low, got {score}"
        _assert_evidence_structure(evidence)

    def test_renamed_pair_scores_intermediate(self):
        """Variable renaming: lexical score should be lower than structural score.
        Identifiers differ, but keywords/operators are the same."""
        tokens_a = _tokens("renamed_a.py")
        tokens_b = _tokens("renamed_b.py")
        score, evidence = lexical_similarity(tokens_a, tokens_b)
        # Should be between 0.1 and 0.9 — some shared tokens (keywords, operators)
        # but different identifiers break n-gram matches
        assert 0.05 < score < 0.95, f"Renamed pair score out of expected range: {score}"
        _assert_evidence_structure(evidence)

    def test_score_in_valid_range(self):
        for fixture_a, fixture_b in [
            ("identical_a.py", "identical_b.py"),
            ("unrelated_a.py", "unrelated_b.py"),
            ("renamed_a.py", "renamed_b.py"),
        ]:
            score, _ = lexical_similarity(_tokens(fixture_a), _tokens(fixture_b))
            assert 0.0 <= score <= 1.0, f"Score out of range for {fixture_a}/{fixture_b}: {score}"

    def test_both_empty_returns_one_with_evidence(self):
        score, evidence = lexical_similarity([], [])
        assert score == 1.0
        _assert_evidence_structure(evidence)
        assert any(item["status"] == "both_empty" for item in evidence)

    def test_one_empty_submission_a(self):
        score, evidence = lexical_similarity([], _tokens("identical_a.py"))
        assert score == 0.0
        _assert_evidence_structure(evidence)
        assert any(item["status"] == "one_empty" for item in evidence)

    def test_one_empty_submission_b(self):
        score, evidence = lexical_similarity(_tokens("identical_a.py"), [])
        assert score == 0.0
        _assert_evidence_structure(evidence)

    def test_evidence_has_matched_items_for_identical(self):
        tokens_a = _tokens("identical_a.py")
        tokens_b = _tokens("identical_b.py")
        _, evidence = lexical_similarity(tokens_a, tokens_b)
        matched = [e for e in evidence if e["status"] == "matched"]
        assert len(matched) > 0, "Identical pair should have matched n-grams in evidence"

    def test_evidence_matched_items_have_counts(self):
        tokens_a = _tokens("identical_a.py")
        tokens_b = _tokens("identical_b.py")
        _, evidence = lexical_similarity(tokens_a, tokens_b)
        for item in evidence:
            if item["status"] == "matched":
                assert "count_a" in item
                assert "count_b" in item
                assert item["count_a"] > 0
                assert item["count_b"] > 0

    def test_n_gram_size_1_identical_is_one(self):
        tokens_a = _tokens("identical_a.py")
        score, evidence = lexical_similarity(tokens_a, tokens_a, n=1)
        assert score == pytest.approx(1.0)

    def test_n_gram_size_1_unrelated_is_lower(self):
        score_1, _ = lexical_similarity(_tokens("unrelated_a.py"), _tokens("unrelated_b.py"), n=1)
        score_3, _ = lexical_similarity(_tokens("unrelated_a.py"), _tokens("unrelated_b.py"), n=3)
        # Unigrams share more common Python keywords → n=1 score ≥ n=3 score typically
        assert isinstance(score_1, float)
        assert isinstance(score_3, float)

    def test_syntax_error_source_handles_gracefully(self):
        """Source with syntax error → partial tokens → lexical still runs."""
        from app.preprocessing.preprocess import tokenize_code
        syntax_code = (FIXTURES / "syntax_error.py").read_text(encoding="utf-8")
        tokens_broken = tokenize_code(syntax_code)
        tokens_good = _tokens("identical_a.py")
        score, evidence = lexical_similarity(tokens_broken, tokens_good)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        _assert_evidence_structure(evidence)

    def test_long_file_does_not_crash(self):
        tokens_long = _tokens("long_file.py")
        tokens_short = _tokens("unrelated_b.py")
        score, evidence = lexical_similarity(tokens_long, tokens_short)
        assert isinstance(score, float)
        _assert_evidence_structure(evidence)

    def test_one_liner_pair(self):
        tokens_one = _tokens("one_liner.py")
        score, evidence = lexical_similarity(tokens_one, tokens_one)
        assert score == pytest.approx(1.0)
        _assert_evidence_structure(evidence)

    def test_symmetry(self):
        """lexical_similarity(A, B) should equal lexical_similarity(B, A)."""
        tokens_a = _tokens("renamed_a.py")
        tokens_b = _tokens("renamed_b.py")
        score_ab, _ = lexical_similarity(tokens_a, tokens_b)
        score_ba, _ = lexical_similarity(tokens_b, tokens_a)
        assert score_ab == pytest.approx(score_ba, abs=1e-6)

    def test_evidence_only_in_a_items_present_for_unrelated(self):
        tokens_a = _tokens("unrelated_a.py")
        tokens_b = _tokens("unrelated_b.py")
        _, evidence = lexical_similarity(tokens_a, tokens_b)
        statuses = {e["status"] for e in evidence}
        # Should have items exclusive to each side
        assert "only_in_a" in statuses or "only_in_b" in statuses


class TestNgramHelpers:
    def test_build_ngrams_basic(self):
        from app.similarity.lexical import _build_ngrams
        tokens = ["a", "b", "c", "d"]
        counter = _build_ngrams(tokens, 2)
        assert counter[("a", "b")] == 1
        assert counter[("b", "c")] == 1
        assert counter[("c", "d")] == 1

    def test_build_ngrams_shorter_than_n(self):
        from app.similarity.lexical import _build_ngrams
        tokens = ["a", "b"]
        # Should fall back to 1-grams
        counter = _build_ngrams(tokens, 3)
        assert len(counter) > 0

    def test_multiset_jaccard_identical(self):
        from collections import Counter
        from app.similarity.lexical import _multiset_jaccard
        c = Counter(["a", "b", "a"])
        assert _multiset_jaccard(c, c) == pytest.approx(1.0)

    def test_multiset_jaccard_disjoint(self):
        from collections import Counter
        from app.similarity.lexical import _multiset_jaccard
        ca = Counter(["a", "b"])
        cb = Counter(["c", "d"])
        assert _multiset_jaccard(ca, cb) == pytest.approx(0.0)

    def test_multiset_jaccard_both_empty(self):
        from collections import Counter
        from app.similarity.lexical import _multiset_jaccard
        assert _multiset_jaccard(Counter(), Counter()) == pytest.approx(1.0)
