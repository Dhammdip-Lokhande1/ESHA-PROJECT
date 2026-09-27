"""
tests/test_structural.py
=========================
Full test suite for similarity/structural.py.

Verifies:
  1. Identical pair → score = 1.0
  2. Unrelated pair → score < 1.0
  3. Renamed pair → high structural score (same shape, different names)
  4. Both None (syntax error) → score = 0.0, evidence explains
  5. One None → score = 0.0, evidence explains
  6. Evidence is always a non-empty list of dicts (Non-Negotiable Rule 2)
  7. Evidence includes subtree-level info (which node types matched/diverged)
     — not just the aggregate edit distance (fixes known prior gap)
  8. Score is in [0.0, 1.0]
  9. Evidence has 'summary' item with edit_distance
 10. Long file → no crash
 11. One-liner → no crash
 12. Empty AST (empty source) → handled
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.preprocessing.preprocess import parse_ast
from app.similarity.structural import (
    structural_similarity,
    _ast_to_zss,
    _count_nodes,
    _node_type_counter,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _ast(name: str) -> ast.AST | None:
    code = (FIXTURES / name).read_text(encoding="utf-8")
    return parse_ast(code)


def _assert_evidence_structure(evidence: list[dict]) -> None:
    assert isinstance(evidence, list), "evidence must be a list"
    assert len(evidence) > 0, "evidence must not be empty (Non-Negotiable Rule 2)"
    for item in evidence:
        assert isinstance(item, dict), f"evidence item must be dict, got {type(item)}"
        assert "node_type" in item, f"missing 'node_type' key in {item}"
        assert "status" in item, f"missing 'status' key in {item}"


class TestStructuralSimilarity:
    def test_identical_pair_scores_one(self):
        ast_a = _ast("identical_a.py")
        ast_b = _ast("identical_b.py")
        score, evidence = structural_similarity(ast_a, ast_b)
        assert score == pytest.approx(1.0), f"Identical pair should score 1.0, got {score}"
        _assert_evidence_structure(evidence)

    def test_unrelated_pair_scores_below_one(self):
        ast_a = _ast("unrelated_a.py")
        ast_b = _ast("unrelated_b.py")
        score, evidence = structural_similarity(ast_a, ast_b)
        assert score < 1.0, f"Unrelated pair should score < 1.0, got {score}"
        assert score >= 0.0
        _assert_evidence_structure(evidence)

    def test_renamed_pair_scores_high(self):
        """Variable renaming: AST shape is identical → should score 1.0 or very close."""
        ast_a = _ast("renamed_a.py")
        ast_b = _ast("renamed_b.py")
        score, evidence = structural_similarity(ast_a, ast_b)
        # Renamed pair has identical structure — only identifier Names differ
        # ZSS label = node class name (not identifier value), so score should be 1.0
        assert score == pytest.approx(1.0, abs=0.05), (
            f"Renamed pair should score ~1.0 structurally, got {score}"
        )
        _assert_evidence_structure(evidence)

    def test_score_in_valid_range(self):
        for fixture_a, fixture_b in [
            ("identical_a.py", "identical_b.py"),
            ("unrelated_a.py", "unrelated_b.py"),
            ("renamed_a.py", "renamed_b.py"),
            ("long_file.py", "unrelated_b.py"),
        ]:
            ast_a = _ast(fixture_a)
            ast_b = _ast(fixture_b)
            score, _ = structural_similarity(ast_a, ast_b)
            assert 0.0 <= score <= 1.0, f"Score out of range for {fixture_a}/{fixture_b}: {score}"

    def test_both_none_returns_zero_with_evidence(self):
        score, evidence = structural_similarity(None, None)
        assert score == 0.0
        _assert_evidence_structure(evidence)
        assert any(item["status"] == "both_syntax_error" for item in evidence)

    def test_none_ast_a_returns_zero(self):
        ast_b = _ast("identical_a.py")
        score, evidence = structural_similarity(None, ast_b)
        assert score == 0.0
        _assert_evidence_structure(evidence)
        assert any(item["status"] == "syntax_error_a" for item in evidence)

    def test_none_ast_b_returns_zero(self):
        ast_a = _ast("identical_a.py")
        score, evidence = structural_similarity(ast_a, None)
        assert score == 0.0
        _assert_evidence_structure(evidence)
        assert any(item["status"] == "syntax_error_b" for item in evidence)

    def test_syntax_error_file_produces_none_ast(self):
        """parse_ast returns None for the syntax-error fixture."""
        result = _ast("syntax_error.py")
        assert result is None

    def test_evidence_has_summary_item(self):
        """Evidence MUST have a summary item with edit_distance (fixes prior gap)."""
        ast_a = _ast("renamed_a.py")
        ast_b = _ast("renamed_b.py")
        _, evidence = structural_similarity(ast_a, ast_b)
        summary_items = [e for e in evidence if e["status"] == "summary"]
        assert len(summary_items) >= 1, "Evidence must have a summary item"
        summary = summary_items[0]
        assert "edit_distance" in summary, "Summary must include edit_distance"
        assert "note" in summary

    def test_evidence_has_subtree_level_detail(self):
        """Evidence must show which subtrees matched/diverged — not just aggregate distance.
        This is the explicit fix for the known prior-build gap."""
        ast_a = _ast("renamed_a.py")
        ast_b = _ast("renamed_b.py")
        _, evidence = structural_similarity(ast_a, ast_b)
        statuses = {e["status"] for e in evidence}
        # Must have at least one subtree-level item (not only the summary)
        assert "matched_subtree" in statuses or "only_in_a" in statuses or "only_in_b" in statuses, (
            "Evidence must include subtree-level items, not just summary. "
            "This fixes the known prior-build gap."
        )

    def test_evidence_matched_subtrees_have_node_type_counts(self):
        ast_a = _ast("identical_a.py")
        ast_b = _ast("identical_b.py")
        _, evidence = structural_similarity(ast_a, ast_b)
        for item in evidence:
            if item["status"] == "matched_subtree":
                assert "count_a" in item
                assert "count_b" in item
                assert item["count_a"] > 0
                assert item["count_b"] > 0

    def test_long_file_does_not_crash(self):
        ast_a = _ast("long_file.py")
        ast_b = _ast("unrelated_b.py")
        score, evidence = structural_similarity(ast_a, ast_b)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        _assert_evidence_structure(evidence)

    def test_one_liner(self):
        ast_a = _ast("one_liner.py")
        score, evidence = structural_similarity(ast_a, ast_a)
        assert score == pytest.approx(1.0)
        _assert_evidence_structure(evidence)

    def test_symmetry(self):
        """structural_similarity(A, B) should equal structural_similarity(B, A)."""
        ast_a = _ast("unrelated_a.py")
        ast_b = _ast("unrelated_b.py")
        score_ab, _ = structural_similarity(ast_a, ast_b)
        score_ba, _ = structural_similarity(ast_b, ast_a)
        assert score_ab == pytest.approx(score_ba, abs=1e-6)

    def test_empty_code_against_valid(self):
        """parse_ast on empty string returns None → graceful handling."""
        ast_empty = parse_ast("")
        ast_valid = _ast("one_liner.py")
        score, evidence = structural_similarity(ast_empty, ast_valid)
        assert score == 0.0
        _assert_evidence_structure(evidence)


class TestAstHelpers:
    def test_count_nodes_basic(self):
        tree = parse_ast("x = 1")
        assert tree is not None
        count = _count_nodes(tree)
        assert count > 0

    def test_count_nodes_empty_module(self):
        tree = parse_ast("pass")
        assert tree is not None
        count = _count_nodes(tree)
        assert count >= 1

    def test_node_type_counter_includes_module(self):
        tree = parse_ast("def foo(): pass")
        assert tree is not None
        counter = _node_type_counter(tree)
        assert "Module" in counter
        assert "FunctionDef" in counter

    def test_ast_to_zss_basic(self):
        tree = parse_ast("x = 1")
        assert tree is not None
        zss_node = _ast_to_zss(tree)
        assert zss_node is not None
        assert zss_node.label == "Module"

    def test_ast_to_zss_function_def(self):
        tree = parse_ast("def foo(x): return x")
        assert tree is not None
        zss_node = _ast_to_zss(tree)
        # Root is Module, one child is FunctionDef
        assert any(
            child.label == "FunctionDef"
            for child in zss_node.children
        )
