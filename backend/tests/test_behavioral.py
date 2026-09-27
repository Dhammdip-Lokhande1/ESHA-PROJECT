"""
tests/test_behavioral.py
========================
Test suite for the behavioral similarity module.

Verifies:
  1. Identical behavior returns score 1.0.
  2. Divergent behavior returns < 1.0.
  3. No test inputs + no auto-gen possible returns None score gracefully.
  4. Auto-generation works for basic function signatures.
  5. Exceptions (like Timeout or TypeError) are captured and matched if identical.
  6. Evidence list contains the expected structure.
"""
from __future__ import annotations

import pytest

from app.similarity.behavioral import behavioral_similarity

# --- Test cases where we explicitly provide inputs ---

def test_identical_behavior():
    code_a = "def add(x, y): return x + y"
    code_b = "def add(a, b):\n  res = a + b\n  return res"
    inputs = ["add(2, 3)", "add(-1, 1)"]
    
    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert score == 1.0
    assert len(evidence) == 2
    for item in evidence:
        assert item["matched"] is True
        assert item["output_a"] == item["output_b"]


def test_divergent_behavior():
    code_a = "def add(x, y): return x + y"
    code_b = "def add(x, y): return x - y"  # Different behavior
    inputs = ["add(2, 3)"]
    
    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert score == 0.0
    assert len(evidence) == 1
    assert evidence[0]["matched"] is False
    assert evidence[0]["output_a"] != evidence[0]["output_b"]


def test_partial_divergence():
    code_a = "def math(x): return x * 2"
    code_b = "def math(x):\n  if x == 0: return 0\n  return x * 3"
    inputs = ["math(0)", "math(2)"]  # math(0) matches, math(2) diverges
    
    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert score == 0.5


def test_exceptions_captured():
    code_a = "def foo(): raise ValueError('bad')"
    code_b = "def foo(): raise ValueError('bad')"
    code_c = "def foo(): raise TypeError('worse')"
    inputs = ["foo()"]
    
    # Identical exception types match
    score_ab, ev_ab = behavioral_similarity(code_a, code_b, inputs)
    assert score_ab == 1.0
    assert "ERROR" in ev_ab[0]["output_a"]
    
    # Different exception types diverge
    score_ac, ev_ac = behavioral_similarity(code_a, code_c, inputs)
    assert score_ac == 0.0
    assert ev_ac[0]["matched"] is False


def test_infinite_loop_timeout(monkeypatch):
    from app.config import settings
    # Patch timeout to be very short for the test
    monkeypatch.setattr(settings, "BEHAVIORAL_TIMEOUT_SECONDS", 0.5)
    
    code_a = "def loop():\n  while True: pass"
    code_b = "def loop():\n  while True: pass"
    inputs = ["loop()"]
    
    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert score == 1.0
    assert "TimeoutExpired" in evidence[0]["output_a"]
    

# --- Test cases for auto-generation ---

def test_auto_generate_no_args():
    code_a = "def main(): return 42"
    code_b = "def main(): return 42"
    score, evidence = behavioral_similarity(code_a, code_b)
    
    assert score == 1.0
    assert len(evidence) == 1
    assert evidence[0]["input"] == "main()"
    assert evidence[0]["output_a"] == "42"


def test_auto_generate_one_arg():
    code_a = "def process(x): return x"
    code_b = "def process(y): return y"
    score, evidence = behavioral_similarity(code_a, code_b)
    
    assert score == 1.0
    # Should generate multiple basic inputs (0, 1, '', [])
    assert len(evidence) >= 1
    assert "process(0)" in [e["input"] for e in evidence]


def test_auto_generate_different_signatures():
    code_a = "def foo(x): pass"
    code_b = "def foo(x, y): pass"  # Arity mismatch
    score, evidence = behavioral_similarity(code_a, code_b)
    
    assert score is None
    assert len(evidence) == 1
    assert evidence[0]["status"] == "skipped"


def test_no_functions_to_auto_generate():
    code_a = "x = 5"
    code_b = "x = 10"
    score, evidence = behavioral_similarity(code_a, code_b)
    
    assert score is None
    assert evidence[0]["status"] == "skipped"


def test_syntax_error_prevents_auto_generate():
    code_a = "def foo(): return 1"
    code_b = "def foo(): print('missing quote)\n"
    score, evidence = behavioral_similarity(code_a, code_b)
    
    assert score is None
    assert evidence[0]["status"] == "skipped"


def test_syntax_error_with_explicit_inputs():
    """Even if there's a syntax error, if explicit inputs are provided, it attempts to run them."""
    code_a = "def foo(): return 1"
    code_b = "def foo(): print('missing quote)\n"
    inputs = ["foo()"]
    
    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert score == 0.0
    assert evidence[0]["matched"] is False
    assert "ERROR" in evidence[0]["output_b"]


def test_blocked_imports():
    """Verify that importing system/network modules triggers a SecurityViolation."""
    code_a = "import os\ndef foo(): return os.getcwd()"
    code_b = "import sys\ndef foo(): return sys.version"
    inputs = ["foo()"]

    score, evidence = behavioral_similarity(code_a, code_b, inputs)
    assert "SecurityViolation" in evidence[0]["output_a"]
    assert "blocked import 'os'" in evidence[0]["output_a"]
    assert "SecurityViolation" in evidence[0]["output_b"]
    assert "blocked import 'sys'" in evidence[0]["output_b"]


def test_sandbox_escape_attempts_blocked():
    """Phase 1 Sandbox Escape Regression Tests: verify attribute walks, dynamic reflection, and pickle are blocked."""
    escape_codes = [
        "def foo():\n for c in ().__class__.__base__.__subclasses__(): pass\n return 1",
        "def foo():\n return getattr(__builtins__, 'eval')('1+1')",
        "def foo():\n return f'{''.__class__.__mro__}'",
        "def foo():\n import pickle\n return pickle.dumps(1)"
    ]
    inputs = ["foo()"]
    for code in escape_codes:
        score, evidence = behavioral_similarity(code, "def foo(): return 1", inputs)
        assert "SecurityViolation" in evidence[0]["output_a"]


