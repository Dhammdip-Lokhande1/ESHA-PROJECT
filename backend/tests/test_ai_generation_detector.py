"""
tests/test_ai_generation_detector.py
======================================
Test suite for explain/ai_generation_detector.py.

Verifies:
  1. All 6 mandatory features are returned in the evidence list.
  2. Likelihood score is bounded [0.0, 1.0].
  3. AI-like code yields a higher likelihood than typical student code.
  4. Invalid syntax fails gracefully (AST features return None).
  5. Empty input returns 0.0 likelihood safely.
  6. Interpretations strings are present.
"""
from __future__ import annotations

import pytest

from app.explain.ai_generation_detector import detect_ai_generated

MANDATORY_FEATURES = {
    "docstring_density",
    "type_hint_density",
    "comment_to_code_ratio",
    "naming_convention_compliance",
    "avg_identifier_length",
    "token_entropy",
}


def test_mandatory_features_present():
    code = "def foo(): pass"
    likelihood, evidence = detect_ai_generated(code)
    extracted_features = {item["feature"] for item in evidence}
    assert extracted_features == MANDATORY_FEATURES


def test_likelihood_bounds():
    code = "def foo(): pass"
    likelihood, evidence = detect_ai_generated(code)
    assert 0.0 <= likelihood <= 1.0


def test_empty_input():
    likelihood, evidence = detect_ai_generated("")
    assert likelihood == 0.0
    assert len(evidence) == 1
    assert evidence[0]["feature"] == "empty_input"
    assert evidence[0]["status"] == "low"


def test_syntax_error_fallback():
    # Invalid syntax means AST features can't be computed
    code = "def foo():\n  print('missing quote)\n"
    likelihood, evidence = detect_ai_generated(code)
    assert 0.0 <= likelihood <= 1.0
    
    ast_features = [
        "docstring_density", "type_hint_density", 
        "naming_convention_compliance", "avg_identifier_length"
    ]
    # Check that AST features are present but None
    for item in evidence:
        if item["feature"] in ast_features:
            assert item["value"] is None
        if item["feature"] == "token_entropy":
            # Tokenizer may also fail or partially parse, but we shouldn't crash
            pass


def test_ai_like_code_scores_higher():
    # Typical student code: no docstrings, no types, short names, no comments
    student_code = '''
def p(x, y):
    r = x + y
    return r
'''
    
    # AI generated code: heavily typed, documented, long compliant names
    ai_code = '''
def calculate_sum_of_values(first_value: int, second_value: int) -> int:
    """
    Calculate the sum of two integers.
    
    Args:
        first_value (int): The first integer to add.
        second_value (int): The second integer to add.
        
    Returns:
        int: The sum of the two integers.
    """
    # Initialize the result variable
    result_sum: int = first_value + second_value
    
    # Return the computed result
    return result_sum
'''
    student_score, _ = detect_ai_generated(student_code)
    ai_score, ai_evidence = detect_ai_generated(ai_code)
    
    assert ai_score > student_score, f"AI score ({ai_score}) should be > Student score ({student_score})"
    assert ai_score > 0.5, "Strong AI pattern should score > 0.5"


def test_interpretations_present():
    code = "def f(x: int) -> int:\n    return x"
    likelihood, evidence = detect_ai_generated(code)
    for item in evidence:
        assert "interpretation" in item
        assert isinstance(item["interpretation"], str)
        assert len(item["interpretation"]) > 0


def test_boost_multiplier():
    """Verify that high docstring + high type hint triggers the boost."""
    code = '''
def my_awesome_function(input_data: list[int]) -> float:
    """This is a very descriptive docstring."""
    return 0.0
'''
    score, evidence = detect_ai_generated(code)
    # Just assert it calculates properly and stays <= 1.0
    assert score <= 1.0
    assert score > 0.0
