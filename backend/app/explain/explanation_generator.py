"""
explain/explanation_generator.py
==================================
Deterministic template-based explanation generator.

Public API (section 8.9 of INSTRUCTIONS.md):

    generate_explanation(
        scores: dict,
        transformation: dict,
        ai_evidence: list[dict]
    ) -> str

Requirements from spec:
  1. MUST reference the actual score values passed in — not a generic sentence.
  2. MUST incorporate AI-generation evidence into the text when relevant —
     not just mention the fusion/structural/lexical scores.
  3. Must use investigative, non-absolute language (section 9.6):
     "this pattern is consistent with..." not "this IS plagiarism".
  4. The one-line verdict form is used as the primary output (section 9.2 item 2)
     with a structured breakdown section appended.
  5. Always deterministic — no randomness, no LLM calls in the core path.
     (Optional LLM polish is on top of this, not replacing it — section 6.)

Templates are defined per transformation type. Each template receives a
context dict built from the actual scores and evidence, so every output
references real numbers.

Design
------
The function returns a structured dict (not just a string) so the API can
render different parts of the explanation at different disclosure levels:
  - 'verdict':    one-line summary (largest text in the UI per section 9.2)
  - 'narrative':  2-3 sentence paragraph expanding on the verdict
  - 'signals':    bullet list of the key evidence drivers
  - 'caveats':    important limitations (missing behavioral, truncation, etc.)
"""
from __future__ import annotations

from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Template helpers
# ──────────────────────────────────────────────────────────────────────────────

def _pct(val: float | None) -> str:
    """Format a [0.0, 1.0] float as a percentage string. None → 'N/A'."""
    if val is None:
        return "N/A"
    return f"{val * 100:.0f}%"


def _conf_label(confidence: float) -> str:
    """Convert numeric confidence to a 3-level label for the UI."""
    if confidence >= 0.70:
        return "high confidence"
    elif confidence >= 0.40:
        return "moderate confidence"
    else:
        return "low confidence"


def _behavioral_note(scores: dict) -> str | None:
    """Return a caveat string about behavioral signal if it was absent."""
    beh = scores.get("behavioral")
    if beh is None:
        return (
            "The behavioral (output-comparison) signal was not computed for this pair. "
            "Conclusions are based on lexical, structural, and semantic analysis only."
        )
    return None


def _semantic_note(scores: dict) -> str | None:
    """Return a caveat if semantic signal was unavailable."""
    sem = scores.get("semantic")
    if sem is None:
        return (
            "The semantic embedding signal was unavailable — "
            "similarity is assessed on lexical and structural patterns only."
        )
    return None


def _ai_note(ai_evidence: list[dict]) -> str | None:
    """
    Produce a 1-sentence AI-generation summary from evidence list.
    Returns None if no AI evidence is present or relevant.
    """
    if not ai_evidence:
        return None
    # Find the status item
    not_implemented = any(
        e.get("status") == "not_implemented" for e in ai_evidence
    )
    if not_implemented:
        return None
    # Summarise key features if present
    high_features = [
        e.get("feature") for e in ai_evidence
        if e.get("status") == "high" or (
            isinstance(e.get("value"), (int, float))
            and e.get("value", 0) > 0.7
        )
    ]
    if high_features:
        feature_str = ", ".join(str(f) for f in high_features[:3])
        return (
            f"The AI-generation detector flagged elevated values for: {feature_str}."
        )
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Per-type templates
# ──────────────────────────────────────────────────────────────────────────────

def _template_exact_copy(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    lex = scores.get("lexical")
    struct = scores.get("structural")
    fusion = scores.get("fusion")
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)

    verdict = (
        f"Likely exact copy — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"This pair shows lexical similarity of {_pct(lex)} and structural similarity "
        f"of {_pct(struct)}, consistent with a direct copy of the source code. "
        f"The token n-gram overlap and AST structure are nearly identical, "
        f"which is the pattern expected when one submission is an unmodified copy of another."
    )
    signals = [
        f"Lexical (n-gram) similarity: {_pct(lex)}",
        f"Structural (AST) similarity: {_pct(struct)}",
        f"Fused similarity: {_pct(fusion)}",
    ]
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


def _template_variable_renaming(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    lex = scores.get("lexical")
    struct = scores.get("structural")
    sem = scores.get("semantic")
    fusion = scores.get("fusion")
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)

    verdict = (
        f"Likely variable renaming — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"The structural similarity ({_pct(struct)}) is substantially higher than "
        f"the lexical similarity ({_pct(lex)}), which is the characteristic pattern "
        f"of identifier substitution: the code's logical structure is preserved "
        f"while variable and function names have been changed."
    )
    if sem is not None:
        narrative += (
            f" Semantic embedding similarity ({_pct(sem)}) further supports "
            f"that both submissions express the same computational intent."
        )
    signals = [
        f"Structural (AST) similarity: {_pct(struct)} — high (structure intact)",
        f"Lexical (n-gram) similarity: {_pct(lex)} — lower (identifiers differ)",
    ]
    if sem is not None:
        signals.append(f"Semantic similarity: {_pct(sem)}")
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


def _template_structural_refactoring(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    struct = scores.get("structural")
    sem = scores.get("semantic")
    lex = scores.get("lexical")
    fusion = scores.get("fusion")
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)

    verdict = (
        f"Likely structural refactoring — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"The structural similarity ({_pct(struct)}) indicates that the code "
        f"organization has been modified — loops restructured, code extracted into "
        f"functions, or control flow rearranged — while the underlying algorithm "
        f"appears similar."
    )
    if sem is not None and sem >= 0.55:
        narrative += (
            f" Semantic similarity ({_pct(sem)}) suggests the computational "
            f"intent is preserved despite structural changes."
        )
    signals = [
        f"Structural (AST) similarity: {_pct(struct)} — moderate",
        f"Lexical (n-gram) similarity: {_pct(lex)}",
    ]
    if sem is not None:
        signals.append(f"Semantic similarity: {_pct(sem)}")
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


def _template_likely_ai_rewrite(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    fusion = scores.get("fusion")
    ai_likelihood = transformation.get("scores_snapshot", {}).get("ai_likelihood", 0.0)
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)
    ai_note = _ai_note(ai_evidence)

    verdict = (
        f"Likely AI-assisted rewrite — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"The AI-generation detector assigned a likelihood of {ai_likelihood:.0%} "
        f"to at least one submission, indicating patterns consistent with "
        f"AI-generated or AI-assisted code."
    )
    if ai_note:
        narrative += f" {ai_note}"
    narrative += (
        f" This does not constitute a definitive finding — the pattern is consistent "
        f"with AI involvement but requires human review of the specific evidence below."
    )
    sem = scores.get("semantic")
    lex = scores.get("lexical")
    struct = scores.get("structural")
    signals = [
        f"AI-generation likelihood: {ai_likelihood:.0%}",
        f"Fused similarity: {_pct(fusion)}",
        f"Lexical similarity: {_pct(lex)}",
        f"Structural similarity: {_pct(struct)}",
    ]
    if sem is not None:
        signals.append(f"Semantic similarity: {_pct(sem)}")
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


def _template_partial_match(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    fusion = scores.get("fusion")
    lex = scores.get("lexical")
    struct = scores.get("structural")
    sem = scores.get("semantic")
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)

    verdict = (
        f"Partial code overlap — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"Some overlapping code fragments were detected (lexical: {_pct(lex)}, "
        f"structural: {_pct(struct)}), but the overall similarity is insufficient "
        f"to establish a clear transformation pattern. "
        f"This may reflect shared library code, common algorithmic patterns, "
        f"or partial copying of specific sections."
    )
    signals = [
        f"Fused similarity: {_pct(fusion)}",
        f"Lexical (n-gram) similarity: {_pct(lex)}",
        f"Structural (AST) similarity: {_pct(struct)}",
    ]
    if sem is not None:
        signals.append(f"Semantic similarity: {_pct(sem)}")
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


def _template_unrelated(scores: dict, transformation: dict, ai_evidence: list[dict]) -> dict:
    fusion = scores.get("fusion")
    conf = transformation.get("confidence", 0.0)
    conf_label = _conf_label(conf)

    verdict = (
        f"Submissions appear unrelated — {_pct(fusion)} overall similarity, {conf_label}."
    )
    narrative = (
        f"All similarity signals are below the meaningful threshold. "
        f"The fused similarity score is {_pct(fusion)}, and no consistent "
        f"lexical, structural, or semantic overlap was detected. "
        f"These submissions are consistent with independent work."
    )
    signals = [
        f"Fused similarity: {_pct(fusion)} — below threshold",
        f"Lexical similarity: {_pct(scores.get('lexical'))}",
        f"Structural similarity: {_pct(scores.get('structural'))}",
    ]
    return {"verdict": verdict, "narrative": narrative, "signals": signals}


# ──────────────────────────────────────────────────────────────────────────────
# Dispatch table
# ──────────────────────────────────────────────────────────────────────────────

_TEMPLATES = {
    "exact_copy": _template_exact_copy,
    "variable_renaming": _template_variable_renaming,
    "structural_refactoring": _template_structural_refactoring,
    "likely_ai_rewrite": _template_likely_ai_rewrite,
    "partial_match": _template_partial_match,
    "unrelated": _template_unrelated,
}


# ──────────────────────────────────────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────────────────────────────────────

def generate_explanation(
    scores: dict[str, float | None],
    transformation: dict[str, Any],
    ai_evidence: list[dict],
) -> dict[str, Any]:
    """
    Generate a structured, deterministic explanation for a similarity result.

    Parameters
    ----------
    scores : dict
        Keys: 'lexical', 'structural', 'semantic', 'behavioral', 'fusion'.
        Values in [0.0, 1.0] or None.
    transformation : dict
        Output of detect_transformation() — must have 'type', 'confidence',
        'rule_matched'.
    ai_evidence : list[dict]
        Output of detect_ai_generated() evidence list.

    Returns
    -------
    dict with keys:
      - transformation_type: str — the classification label
      - confidence: float — in [0.0, 1.0]
      - verdict: str — one-line summary referencing actual scores (required by spec)
      - narrative: str — 2-3 sentence paragraph
      - signals: list[str] — bullet-ready evidence lines
      - caveats: list[str] — limitations/missing signals
      - rule_matched: str — from transformation detector

    The 'verdict' field is the primary display string per section 9.2 item 2.
    Every string in this output references actual score values, not generic placeholders.
    """
    transformation_type = transformation.get("type", "unrelated")
    template_fn = _TEMPLATES.get(transformation_type, _template_unrelated)

    # Get the type-specific content
    content = template_fn(scores, transformation, ai_evidence)

    # Build caveats list — always check for missing signals
    caveats: list[str] = []
    beh_note = _behavioral_note(scores)
    if beh_note:
        caveats.append(beh_note)
    sem_note = _semantic_note(scores)
    if sem_note:
        caveats.append(sem_note)

    # Section 9.6 mandatory caveat — always append
    caveats.append(
        "This analysis is advisory only. The patterns described are consistent with "
        "the indicated transformation type but require human review before any "
        "academic integrity conclusion is drawn."
    )

    return {
        "transformation_type": transformation_type,
        "confidence": transformation.get("confidence", 0.0),
        "verdict": content["verdict"],
        "narrative": content["narrative"],
        "signals": content["signals"],
        "caveats": caveats,
        "rule_matched": transformation.get("rule_matched", ""),
    }
