"""
explain/confidence.py
======================
Confidence indicator calculation per dimension (section 9.3 of INSTRUCTIONS.md).

Returns a dictionary mapping each dimension to 'high', 'medium', or 'low':
  - 'high': score is well-supported (substantial code, full AST, un-truncated model, multiple tests)
  - 'medium': moderate support (shorter code, truncated embedding, single test case)
  - 'low': thin support (very short 1-liner, syntax error, no behavioral tests executed)
"""
from __future__ import annotations

import ast
from typing import Any


def compute_confidence_indicators(
    tokens_a: list[str],
    tokens_b: list[str],
    ast_a: ast.AST | None,
    ast_b: ast.AST | None,
    sem_score: float | None,
    sem_evidence: list[dict[str, Any]],
    beh_score: float | None,
    beh_evidence: list[dict[str, Any]],
) -> dict[str, str]:
    """
    Calculate confidence indicators ('high' | 'medium' | 'low') for each dimension.
    """
    total_tokens = len(tokens_a) + len(tokens_b)

    # 1. Lexical confidence
    if total_tokens >= 40:
        lex_conf = "high"
    elif total_tokens >= 15:
        lex_conf = "medium"
    else:
        lex_conf = "low"

    # 2. Structural confidence
    if ast_a is not None and ast_b is not None:
        # Check node count if available
        count_a = sum(1 for _ in ast.walk(ast_a))
        count_b = sum(1 for _ in ast.walk(ast_b))
        if count_a >= 8 and count_b >= 8:
            struct_conf = "high"
        else:
            struct_conf = "medium"
    else:
        # Syntax error on one or both files
        struct_conf = "low"

    # 3. Semantic confidence
    if sem_score is None:
        sem_conf = "low"
    else:
        # Check if truncated
        is_truncated = any(
            item.get("type") == "truncation_disclosure" and item.get("file") in ("a", "b")
            for item in sem_evidence
        )
        if is_truncated:
            sem_conf = "medium"
        else:
            sem_conf = "high"

    # 4. Behavioral confidence
    if beh_score is None:
        beh_conf = "low"
    else:
        test_count = sum(1 for item in beh_evidence if "input" in item or "inputs" in item)
        if test_count >= 2:
            beh_conf = "high"
        elif test_count == 1:
            beh_conf = "medium"
        else:
            beh_conf = "medium" if beh_score is not None else "low"

    return {
        "lexical": lex_conf,
        "structural": struct_conf,
        "semantic": sem_conf,
        "behavioral": beh_conf,
    }
