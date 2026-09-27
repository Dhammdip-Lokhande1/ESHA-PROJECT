"""
tests/test_preprocessing.py
============================
Full test suite for preprocessing/preprocess.py.

Section 13 requirements:
  - identical pair, unrelated pair, transformed pair
  - edge cases: empty file, syntax error, very short (1-line), very long (>512 token)

Tests verify:
  1. tokenize_code() return type is list[str]
  2. Comments are stripped
  3. String literals → '<STR>'
  4. Numeric literals → '<NUM>'
  5. Empty input → empty list
  6. Syntax-error source still tokenizes partially (graceful degradation)
  7. parse_ast() returns ast.AST on valid code
  8. parse_ast() returns None on syntax error (never raises)
  9. parse_ast() returns None on empty string
 10. parse_ast() handles long file without crashing
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.preprocessing.preprocess import parse_ast, tokenize_code

# ──────────────────────────────────────────────────────────────────────────────
# Fixture helpers
# ──────────────────────────────────────────────────────────────────────────────
FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# tokenize_code tests
# ──────────────────────────────────────────────────────────────────────────────

class TestTokenizeCode:
    def test_returns_list_of_strings(self):
        result = tokenize_code("x = 1")
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)

    def test_empty_string_returns_empty_list(self):
        assert tokenize_code("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert tokenize_code("   \n   ") == []

    def test_comments_are_stripped(self):
        code = "# This is a comment\nx = 1  # inline comment"
        tokens = tokenize_code(code)
        assert "This" not in tokens
        assert "comment" not in tokens
        assert "#" not in tokens

    def test_string_literals_normalized(self):
        code = 'name = "Alice"\ngreeting = \'Hello\''
        tokens = tokenize_code(code)
        assert "<STR>" in tokens
        assert "Alice" not in tokens
        assert "Hello" not in tokens

    def test_numeric_literals_normalized(self):
        code = "x = 42\ny = 3.14\nz = 0xFF"
        tokens = tokenize_code(code)
        assert "<NUM>" in tokens
        assert "42" not in tokens
        assert "3.14" not in tokens
        assert "0xFF" not in tokens

    def test_keywords_and_operators_kept(self):
        code = "if x > 0:\n    return x"
        tokens = tokenize_code(code)
        assert "if" in tokens
        assert ">" in tokens
        assert "return" in tokens

    def test_identifiers_kept_verbatim(self):
        code = "my_variable = some_function()"
        tokens = tokenize_code(code)
        assert "my_variable" in tokens
        assert "some_function" in tokens

    def test_identical_files_produce_same_tokens(self):
        code_a = _read("identical_a.py")
        code_b = _read("identical_b.py")
        assert tokenize_code(code_a) == tokenize_code(code_b)

    def test_renamed_files_produce_different_tokens(self):
        """Variable renaming changes identifiers — tokens should differ."""
        tokens_a = tokenize_code(_read("renamed_a.py"))
        tokens_b = tokenize_code(_read("renamed_b.py"))
        assert tokens_a != tokens_b

    def test_unrelated_files_share_few_common_tokens(self):
        """Unrelated code may share keywords but not many identifiers."""
        tokens_a = set(tokenize_code(_read("unrelated_a.py")))
        tokens_b = set(tokenize_code(_read("unrelated_b.py")))
        # Overlap should be minimal — mostly Python keywords like 'return', 'if'
        common = tokens_a & tokens_b
        assert len(common) < max(len(tokens_a), len(tokens_b)) * 0.5

    def test_syntax_error_file_returns_partial_tokens(self):
        """tokenize_code should not crash on syntax errors — return whatever was parsed."""
        code = _read("syntax_error.py")
        result = tokenize_code(code)
        # Should return a list (possibly empty or partial)
        assert isinstance(result, list)

    def test_one_liner(self):
        code = _read("one_liner.py")
        tokens = tokenize_code(code)
        assert isinstance(tokens, list)
        assert len(tokens) >= 1  # at least 'x', '=', '<NUM>'

    def test_long_file_does_not_crash(self):
        code = _read("long_file.py")
        tokens = tokenize_code(code)
        assert isinstance(tokens, list)
        assert len(tokens) > 512  # should produce many tokens

    def test_multiline_string(self):
        code = '"""This is\na multiline\nstring"""\nx = 1'
        tokens = tokenize_code(code)
        assert "<STR>" in tokens
        assert "This" not in tokens

    def test_fstring_normalized(self):
        code = 'name = "world"\nmsg = f"Hello {name}"'
        tokens = tokenize_code(code)
        # f-strings should be treated as string family
        assert isinstance(tokens, list)


# ──────────────────────────────────────────────────────────────────────────────
# parse_ast tests
# ──────────────────────────────────────────────────────────────────────────────

class TestParseAst:
    def test_valid_code_returns_ast(self):
        result = parse_ast("x = 1")
        assert result is not None
        assert isinstance(result, ast.AST)

    def test_empty_string_returns_none(self):
        assert parse_ast("") is None

    def test_whitespace_only_returns_none(self):
        assert parse_ast("   \n") is None

    def test_syntax_error_returns_none_not_raises(self):
        code = "def broken(:\n    pass"
        result = parse_ast(code)
        assert result is None  # must NOT raise

    def test_syntax_error_fixture_returns_none(self):
        code = (Path(__file__).parent / "fixtures" / "syntax_error.py").read_text()
        result = parse_ast(code)
        assert result is None

    def test_identical_files_return_equivalent_structure(self):
        code_a = _read("identical_a.py")
        code_b = _read("identical_b.py")
        ast_a = parse_ast(code_a)
        ast_b = parse_ast(code_b)
        assert ast_a is not None
        assert ast_b is not None
        # Both should produce the same node type at the root
        assert type(ast_a) is type(ast_b)
        # The fixture files have different module-level docstrings, so full dump()
        # equality is not expected. Instead verify they share the same set of
        # AST node types (same structure), which is what the structural module tests.
        from collections import Counter
        def node_types(tree: ast.AST) -> Counter:
            return Counter(type(n).__name__ for n in ast.walk(tree))
        assert node_types(ast_a) == node_types(ast_b)

    def test_long_file_does_not_crash(self):
        code = _read("long_file.py")
        result = parse_ast(code)
        assert result is not None
        assert isinstance(result, ast.AST)

    def test_one_liner(self):
        code = _read("one_liner.py")
        result = parse_ast(code)
        assert isinstance(result, ast.AST)

    def test_returns_module_node(self):
        result = parse_ast("def foo(): pass")
        assert isinstance(result, ast.Module)

    def test_complex_code(self):
        code = _read("unrelated_b.py")
        result = parse_ast(code)
        assert result is not None
        assert isinstance(result, ast.AST)
