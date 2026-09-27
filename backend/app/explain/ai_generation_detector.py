"""
explain/ai_generation_detector.py
===================================
AST + statistical heuristic AI-generation detector.

Public API (section 8.6 of INSTRUCTIONS.md):

    detect_ai_generated(code: str) -> tuple[float, list[dict]]

Computes a weighted likelihood [0.0, 1.0] of code being AI-generated, based on
6 mandatory features:
  1. docstring_density
  2. type_hint_density
  3. avg_identifier_length
  4. naming_convention_compliance
  5. token_entropy
  6. comment_to_code_ratio

Returns the overall likelihood and a detailed evidence list, with one item per
feature containing {feature, value, interpretation}.

Design Notes:
-------------
- AI code tends to be highly documented (high docstring/comment ratio),
  fully type-hinted, compliant with PEP-8 (naming conventions), and uses
  longer, more descriptive variable names than typical student code.
- Entropy measures vocabulary variety: AI code can sometimes be repetitive
  or use a highly standardized vocabulary.
- If the code cannot be parsed (SyntaxError), AST-based features are skipped
  and we fall back to lexical features only.
- Never returns a bare float (Rule 2).
"""
from __future__ import annotations

import ast
import io
import math
import re
import tokenize
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Heuristic extractors
# ──────────────────────────────────────────────────────────────────────────────

def _get_lexical_features(code: str) -> dict[str, float]:
    """Extract comment_to_code_ratio and token_entropy via tokenize."""
    if not code or not code.strip():
        return {"comment_to_code_ratio": 0.0, "token_entropy": 0.0}

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError):
        return {"comment_to_code_ratio": 0.0, "token_entropy": 0.0}

    code_lines = set()
    comment_lines = set()
    token_counts: dict[str, int] = {}
    total_tokens = 0

    for tok in tokens:
        # 1. Comment vs Code counting
        if tok.type == tokenize.COMMENT:
            comment_lines.add(tok.start[0])
        elif tok.type not in (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT,
                              tokenize.DEDENT, tokenize.ENDMARKER):
            code_lines.add(tok.start[0])

        # 2. Entropy prep (ignore structural tokens for entropy)
        if tok.type in (tokenize.NAME, tokenize.OP, tokenize.STRING, tokenize.NUMBER):
            val = tok.string
            token_counts[val] = token_counts.get(val, 0) + 1
            total_tokens += 1

    code_count = len(code_lines)
    comment_count = len(comment_lines)
    ratio = comment_count / code_count if code_count > 0 else 0.0

    # Entropy calculation: -sum(p * log2(p))
    entropy = 0.0
    if total_tokens > 0:
        for count in token_counts.values():
            p = count / total_tokens
            entropy -= p * math.log2(p)

    # Normalize entropy to [0, 1] loosely based on typical max (say, 8.0 bits)
    norm_entropy = min(1.0, entropy / 8.0)

    return {
        "comment_to_code_ratio": ratio,
        "token_entropy": norm_entropy,
    }


def _get_ast_features(code: str) -> dict[str, float | None]:
    """Extract AST-based features. Returns None values if syntax is invalid."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "docstring_density": None,
            "type_hint_density": None,
            "avg_identifier_length": None,
            "naming_convention_compliance": None,
        }

    # 1. Docstring density
    funcs_and_classes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    has_docstring = sum(1 for n in funcs_and_classes if ast.get_docstring(n))
    doc_density = has_docstring / len(funcs_and_classes) if funcs_and_classes else 0.0

    # 2. Type hint density
    annotated = 0
    total_annots = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_annots += len(node.args.args) + 1  # +1 for return type
            annotated += sum(1 for arg in node.args.args if arg.annotation)
            if node.returns:
                annotated += 1
        elif isinstance(node, ast.AnnAssign):
            total_annots += 1
            annotated += 1
        elif isinstance(node, ast.Assign):
            # Normal assignment (unannotated)
            total_annots += len(node.targets)

    type_density = annotated / total_annots if total_annots > 0 else 0.0

    # 3. Identifiers (length + PEP-8 compliance)
    identifiers = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            identifiers.add((node.name, "def"))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            identifiers.add((node.id, "var"))
        elif isinstance(node, ast.arg):
            identifiers.add((node.arg, "var"))

    total_len = sum(len(name) for name, _ in identifiers)
    avg_len = total_len / len(identifiers) if identifiers else 0.0

    # Normalize avg_len to [0, 1] (cap at 20 chars)
    norm_len = min(1.0, avg_len / 20.0)

    # PEP-8 compliance check
    pep8_compliant = 0
    snake_case = re.compile(r"^[a-z_][a-z0-9_]*$")
    camel_case = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
    
    for name, kind in identifiers:
        if name.startswith("__") and name.endswith("__"):
            pep8_compliant += 1
        elif kind == "def" and name[0].isupper(): # basic check for Classes usually being CapWords
            # Strictly we should separate ClassDef from FunctionDef, but simple check:
            if camel_case.match(name) or snake_case.match(name):
                pep8_compliant += 1
        else:
            if snake_case.match(name):
                pep8_compliant += 1
                
    pep8_density = pep8_compliant / len(identifiers) if identifiers else 1.0

    return {
        "docstring_density": doc_density,
        "type_hint_density": type_density,
        "avg_identifier_length": norm_len,
        "raw_avg_len": avg_len,  # stored for interpretation
        "naming_convention_compliance": pep8_density,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Likelihood Scoring & Interpretation
# ──────────────────────────────────────────────────────────────────────────────

# Typical weights for an AI signature. Adjust as needed.
FEATURE_WEIGHTS = {
    "docstring_density": 0.25,
    "type_hint_density": 0.25,
    "comment_to_code_ratio": 0.20,
    "naming_convention_compliance": 0.15,
    "avg_identifier_length": 0.10,
    "token_entropy": 0.05,
}

def _interpret(feature: str, value: float | None, raw_val: float = None) -> str:
    """Provide a human-readable interpretation of the feature value."""
    if value is None:
        return f"{feature} could not be computed (e.g., due to a syntax error)."
        
    if feature == "docstring_density":
        return f"{value*100:.0f}% of functions/classes have docstrings (AI tends to over-document)."
    elif feature == "type_hint_density":
        return f"{value*100:.0f}% of applicable variables/arguments have type hints (AI heavily uses them)."
    elif feature == "comment_to_code_ratio":
        return f"Ratio of comment lines to code is {value:.2f} (AI often produces dense commentary)."
    elif feature == "naming_convention_compliance":
        return f"{value*100:.0f}% of identifiers follow PEP-8 conventions (AI is strictly compliant)."
    elif feature == "avg_identifier_length":
        r = raw_val if raw_val is not None else (value * 20.0)
        return f"Average identifier length is {r:.1f} chars (AI favors long, descriptive names)."
    elif feature == "token_entropy":
        return f"Normalized vocabulary entropy is {value:.2f} (AI can be highly standardized)."
    return ""


# ──────────────────────────────────────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────────────────────────────────────

def detect_ai_generated(code: str) -> tuple[float, list[dict[str, Any]]]:
    """
    Detect likelihood of AI generation based on AST and lexical heuristics.

    Returns
    -------
    likelihood : float
        [0.0, 1.0] value indicating confidence of AI generation.
    evidence : list[dict]
        Feature-by-feature breakdown and interpretation.
    """
    if not code or not code.strip():
        return 0.0, [
            {
                "feature": "empty_input",
                "value": 0.0,
                "interpretation": "Code is empty. AI likelihood is 0.0.",
                "status": "low",
            }
        ]

    lexical = _get_lexical_features(code)
    ast_feat = _get_ast_features(code)

    features = {**lexical, **ast_feat}
    evidence = []
    
    # Calculate weighted likelihood, ignoring None features (SyntaxError fallback)
    total_weight = 0.0
    score = 0.0
    
    for key, weight in FEATURE_WEIGHTS.items():
        val = features.get(key)
        
        status = "unknown"
        if val is not None:
            # AI patterns usually map to high values for these specific normalized features
            status = "high" if val > 0.6 else ("low" if val < 0.3 else "moderate")
            score += val * weight
            total_weight += weight
            
        raw_val = features.get("raw_avg_len") if key == "avg_identifier_length" else None
        
        evidence.append({
            "feature": key,
            "value": round(val, 4) if val is not None else None,
            "status": status,
            "interpretation": _interpret(key, val, raw_val)
        })

    likelihood = score / total_weight if total_weight > 0 else 0.0
    
    # Boost if multiple strong AI signatures align (e.g. high docstrings AND high types)
    doc_dens = ast_feat.get("docstring_density") or 0.0
    type_dens = ast_feat.get("type_hint_density") or 0.0
    if doc_dens > 0.8 and type_dens > 0.7:
        likelihood = min(1.0, likelihood * 1.2)
        
    return round(likelihood, 4), evidence
