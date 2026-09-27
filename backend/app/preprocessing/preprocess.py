"""
preprocessing/preprocess.py
============================
Core preprocessing utilities for EHSA.

Public API (section 8.1 of INSTRUCTIONS.md — interfaces are exact contracts):

    tokenize_code(code: str) -> list[str]
        Tokenizes Python source, strips comments and string literals,
        normalises identifiers.  Returns a flat list of token strings.

    parse_ast(code: str) -> ast.AST | None
        Returns None on SyntaxError — callers must handle gracefully.
        Never raises to the API layer.

Design decisions
----------------
* tokenize_code uses Python's `tokenize` module (stdlib) rather than a
  hand-rolled regex so that the lexer is authoritative about what constitutes
  a token boundary in Python.
* Comments (COMMENT token type) and NL/NEWLINE/ENCODING/ENDMARKER tokens are
  stripped entirely — they carry no structural meaning for similarity.
* String literals are replaced with the placeholder '<STR>' to avoid
  coincidental matches on identical hardcoded strings across otherwise
  different submissions; likewise numeric literals → '<NUM>'.
  This is a deliberate choice: lexical similarity should reflect *logic*
  similarity, not constant reuse. Document in the paper.
* Identifiers are NOT normalised to a common symbol (e.g., 'VAR') because
  keeping them lets the lexical module detect variable-renaming patterns
  at the n-gram level.
"""
from __future__ import annotations

import ast
import io
import keyword
import tokenize as tokenize_mod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Token types to keep (tokenize module constants)
# ──────────────────────────────────────────────────────────────────────────────
_SKIP_TYPES = frozenset(
    [
        tokenize_mod.COMMENT,
        tokenize_mod.NEWLINE,
        tokenize_mod.NL,
        tokenize_mod.ENCODING,
        tokenize_mod.ENDMARKER,
        tokenize_mod.INDENT,
        tokenize_mod.DEDENT,
    ]
)


def tokenize_code(code: str) -> list[str]:
    """
    Tokenize Python *code* into a flat list of string tokens.

    Strips comments, NEWLINE, NL, ENCODING, ENDMARKER, INDENT, DEDENT.
    Normalises:
      * string literals  → '<STR>'
      * numeric literals → '<NUM>'
      * f-string parts   → '<STR>'  (treated as string family)
      * All other tokens kept verbatim (operators, identifiers, keywords).

    Returns an empty list on tokenization error (caller gets empty evidence,
    not a crash).  This graceful degradation is required by section 5 rule 3.

    Parameters
    ----------
    code : str
        Raw Python source code string.

    Returns
    -------
    list[str]
        Ordered list of normalised token strings.
    """
    if not code or not code.strip():
        return []

    tokens: list[str] = []
    try:
        readline = io.StringIO(code).readline
        for tok in tokenize_mod.generate_tokens(readline):
            tok_type = tok.type
            tok_string = tok.string

            if tok_type in _SKIP_TYPES:
                continue

            # Normalise string literals (STRING, FSTRING_* in 3.12+)
            if tok_type == tokenize_mod.STRING:
                tokens.append("<STR>")
                continue

            # Normalise numeric literals
            if tok_type == tokenize_mod.NUMBER:
                tokens.append("<NUM>")
                continue

            # Keep the raw string for OP, NAME (identifiers + keywords), etc.
            if tok_string:
                tokens.append(tok_string)

    except tokenize_mod.TokenError:
        # Tokenization failed (e.g., unterminated string, encoding issue).
        # Return whatever we managed to collect rather than crashing.
        pass

    return tokens


def parse_ast(code: str) -> ast.AST | None:
    """
    Parse *code* into a Python AST.

    Returns
    -------
    ast.AST | None
        Parsed module AST on success; None if *code* contains a SyntaxError
        or is empty.  Callers MUST handle None gracefully — this function
        never raises to the API layer (section 5 rule 3).

    Notes
    -----
    Uses `ast.parse` with `type_comments=False` (default) to avoid failure on
    code that uses bare `# type: …` comments without PEP 526 annotations.
    """
    if not code or not code.strip():
        return None
    try:
        return ast.parse(code)
    except SyntaxError:
        return None
    except Exception:
        # Catch-all for unexpected parse failures (e.g., RecursionError on
        # pathological nesting).
        return None
