"""
similarity/structural.py
=========================
Structural similarity via Zhang-Shasha tree edit distance on Python ASTs.

Public API (section 8.3 of INSTRUCTIONS.md):

    structural_similarity(
        ast_a: ast.AST | None,
        ast_b: ast.AST | None
    ) -> tuple[float, list[dict]]

Non-Negotiable Rule 2: evidence MUST include which subtrees matched/diverged,
not just the aggregate distance. A known gap from a prior build — fixed here.

Algorithm
---------
1. Convert each ast.AST into a `zss.Node` tree (label = AST node type name).
2. Compute ZSS tree edit distance.
3. Normalize: score = 1 - (edit_distance / max_possible_edits).
   max_possible_edits = size(A) + size(B)  (worst case: delete A, insert B).
4. Evidence:
   - List the top matched subtree types (node labels that appear in both trees)
     sorted by frequency — this directly answers "which structural patterns are shared."
   - List node types that appear in A but not B, and vice-versa — structural divergence.
   - Include the raw edit distance and tree sizes.

Design choices
--------------
* Node label = AST node class name (e.g. 'FunctionDef', 'For', 'If').
  We intentionally drop identifier names and literal values from labels so
  that the structural channel measures *shape*, not lexical content. That is
  the correct separation: lexical.py handles naming patterns, structural.py
  handles code shape.
* `zss` implements Zhang-Shasha; this is the correct algorithm per spec
  (section 6 of INSTRUCTIONS.md: "never hand-roll this").
* For None inputs (SyntaxError cases), we return (0.0, evidence_explaining_why)
  rather than raising — callers must handle gracefully (section 5, rule 3).
* Evidence subtree matching is done via node-type multiset comparison rather
  than the actual ZSS edit alignment output (ZSS's public API doesn't expose
  the alignment). The multiset approach is an approximation but is accurate
  for the "which patterns are shared" question and avoids a deep ZSS fork.
"""
from __future__ import annotations

import ast
from collections import Counter
from typing import Any

import zss


# ──────────────────────────────────────────────────────────────────────────────
# AST → zss.Node conversion
# ──────────────────────────────────────────────────────────────────────────────

SKIP_ZSS_WRAPPER_NODES = {
    "Load", "Store", "Del", "Param", "keyword", "alias", "withitem", "ctx"
}


def _ast_to_zss(node: ast.AST) -> zss.Node:
    """
    Recursively convert a Python AST node into a zss.Node tree.

    Label strategy: use the AST node class name (e.g., 'FunctionDef', 'If').
    Children: all child fields that are AST nodes or lists of AST nodes.
    Non-AST fields and noisy context wrapper nodes are dropped — structural shape only.
    """
    label = type(node).__name__
    zss_node = zss.Node(label)

    for field_name, field_value in ast.iter_fields(node):
        if isinstance(field_value, ast.AST):
            if type(field_value).__name__ not in SKIP_ZSS_WRAPPER_NODES:
                zss_node.addkid(_ast_to_zss(field_value))
        elif isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, ast.AST):
                    if type(item).__name__ not in SKIP_ZSS_WRAPPER_NODES:
                        zss_node.addkid(_ast_to_zss(item))

    return zss_node


def _count_nodes(node: ast.AST) -> int:
    """Return the total number of AST nodes in the subtree rooted at *node*."""
    return sum(1 for _ in ast.walk(node))


def _node_type_counter(node: ast.AST) -> Counter[str]:
    """Return a Counter of AST node class names in the subtree."""
    return Counter(type(n).__name__ for n in ast.walk(node))


# ──────────────────────────────────────────────────────────────────────────────
# Evidence builder
# ──────────────────────────────────────────────────────────────────────────────

def _build_structural_evidence(
    ast_a: ast.AST,
    ast_b: ast.AST,
    edit_distance: float,
    size_a: int,
    size_b: int,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """
    Build evidence list for structural similarity.

    Evidence items:
      - One 'summary' item with raw edit_distance, tree sizes, and score.
      - Up to top_n 'matched_subtree' items — node types present in both trees,
        sorted by min-count descending (strongest structural matches first).
      - Up to top_n // 2 'only_in_a' and 'only_in_b' items showing structural
        divergence.

    This directly fulfils the spec requirement:
    "Evidence MUST include which subtrees matched/diverged — not just the
    aggregate distance."
    """
    evidence: list[dict[str, Any]] = []

    counter_a = _node_type_counter(ast_a)
    counter_b = _node_type_counter(ast_b)
    all_types = set(counter_a) | set(counter_b)

    matched = []
    only_a = []
    only_b = []

    for node_type in all_types:
        ca = counter_a[node_type]
        cb = counter_b[node_type]
        if ca > 0 and cb > 0:
            matched.append(
                {
                    "node_type": node_type,
                    "count_a": ca,
                    "count_b": cb,
                    "status": "matched_subtree",
                }
            )
        elif ca > 0:
            only_a.append(
                {
                    "node_type": node_type,
                    "count_a": ca,
                    "count_b": 0,
                    "status": "only_in_a",
                }
            )
        else:
            only_b.append(
                {
                    "node_type": node_type,
                    "count_a": 0,
                    "count_b": cb,
                    "status": "only_in_b",
                }
            )

    matched.sort(key=lambda x: min(x["count_a"], x["count_b"]), reverse=True)
    only_a.sort(key=lambda x: x["count_a"], reverse=True)
    only_b.sort(key=lambda x: x["count_b"], reverse=True)

    evidence.append(
        {
            "node_type": "<summary>",
            "count_a": size_a,
            "count_b": size_b,
            "status": "summary",
            "edit_distance": edit_distance,
            "note": (
                f"ZSS tree edit distance = {edit_distance}. "
                f"Tree A has {size_a} nodes, Tree B has {size_b} nodes."
            ),
        }
    )

    evidence.extend(matched[:top_n])

    if len(matched) > top_n:
        evidence.append(
            {
                "node_type": "<summary>",
                "count_a": None,
                "count_b": None,
                "status": "additional_matched_count",
                "additional_matched": len(matched) - top_n,
            }
        )

    half = max(top_n // 2, 3)
    evidence.extend(only_a[:half])
    evidence.extend(only_b[:half])

    return evidence


# ──────────────────────────────────────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────────────────────────────────────

def structural_similarity(
    ast_a: ast.AST | None,
    ast_b: ast.AST | None,
    top_n: int = 10,
) -> tuple[float, list[dict[str, Any]]]:
    """
    Compute ZSS tree edit distance similarity between two Python ASTs.

    Parameters
    ----------
    ast_a, ast_b : ast.AST | None
        Output of ``preprocessing.preprocess.parse_ast``.  None means the
        source had a SyntaxError.
    top_n : int
        Number of top matched subtree types to include in evidence.

    Returns
    -------
    score : float
        Normalised similarity in [0.0, 1.0].
        1 - (edit_distance / (size_a + size_b)).
        Edge cases:
          - Both None → (0.0, evidence noting both had syntax errors)
          - One None → (0.0, evidence noting which had a syntax error)
          - Both have 0 nodes → (1.0, evidence noting both empty)
    evidence : list[dict]
        Subtree-level evidence — which node types matched/diverged.
        NEVER returns a bare float without this list (Non-Negotiable Rule 2).
    """
    # ── Handle None inputs ─────────────────────────────────────────────────
    if ast_a is None and ast_b is None:
        return 0.0, [
            {
                "node_type": "<error>",
                "count_a": 0,
                "count_b": 0,
                "status": "both_syntax_error",
                "note": "Both submissions had syntax errors — structural similarity is 0.0.",
            }
        ]

    if ast_a is None:
        return 0.0, [
            {
                "node_type": "<error>",
                "count_a": 0,
                "count_b": _count_nodes(ast_b),
                "status": "syntax_error_a",
                "note": "Submission A had a syntax error — structural similarity is 0.0.",
            }
        ]

    if ast_b is None:
        return 0.0, [
            {
                "node_type": "<error>",
                "count_a": _count_nodes(ast_a),
                "count_b": 0,
                "status": "syntax_error_b",
                "note": "Submission B had a syntax error — structural similarity is 0.0.",
            }
        ]

    # ── Build zss trees ────────────────────────────────────────────────────
    size_a = _count_nodes(ast_a)
    size_b = _count_nodes(ast_b)

    if size_a == 0 and size_b == 0:
        return 1.0, [
            {
                "node_type": "<summary>",
                "count_a": 0,
                "count_b": 0,
                "status": "both_empty",
                "note": "Both ASTs have 0 nodes — identical by convention.",
            }
        ]

    zss_a = _ast_to_zss(ast_a)
    zss_b = _ast_to_zss(ast_b)

    # ZSS tree edit distance (unit costs: insert=1, delete=1, update=1)
    edit_distance: float = zss.simple_distance(zss_a, zss_b)

    # Normalise — max possible edits = delete all of A + insert all of B
    max_edits = size_a + size_b
    if max_edits == 0:
        score = 1.0
    else:
        raw_score = max(0.0, 1.0 - (edit_distance / max_edits))
        # Non-linear scaling (power of 3) to suppress weak structural matches
        # (e.g. sharing only boilerplate like FunctionDef and Return).
        score = raw_score ** 3.0

    evidence = _build_structural_evidence(
        ast_a, ast_b, edit_distance, size_a, size_b, top_n=top_n
    )

    return round(score, 6), evidence
