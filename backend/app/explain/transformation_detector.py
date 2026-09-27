"""
explain/transformation_detector.py
====================================
Rule-based transformation type classifier.

Public API (section 8.8 of INSTRUCTIONS.md):

    detect_transformation(scores: dict, ai_likelihood: float) -> dict

    Returns {type, confidence, rule_matched}

    Categories (spec-mandated, section 9.2):
      - 'exact_copy'            — lexical + structural both very high
      - 'variable_renaming'     — structure same, identifiers differ
      - 'structural_refactoring'— meaningful structural changes but same intent
      - 'likely_ai_rewrite'     — AI detector signals high likelihood
      - 'partial_match'         — moderate similarity, unclear pattern
      - 'unrelated'             — no meaningful similarity detected

CRITICAL FIX (AGENTS.md non-negotiable): A prior build had an AI detector
that never fed into the transformation categories. This implementation
explicitly checks ai_likelihood FIRST (if it clears the threshold) so that
'likely_ai_rewrite' is a real classification path — not a dead end.

Rule evaluation order (priority highest → lowest):
  1. likely_ai_rewrite  — ai_likelihood overrides if above threshold
  2. exact_copy         — both lexical ≥ 0.92 AND structural ≥ 0.92
  3. variable_renaming  — structural ≥ 0.88 AND lexical < 0.75
  4. structural_refactoring — structural in [0.55, 0.88) AND
                               (semantic ≥ 0.60 OR lexical ≥ 0.45)
  5. partial_match      — fused OR any dimension score ≥ 0.30
  6. unrelated          — fallback

Design notes
------------
* All thresholds are constants at the top of this file — not scattered
  magic numbers — so they can be adjusted for ablation studies.
* 'confidence' is a float in [0.0, 1.0] derived from how far the
  triggering scores are from the decision boundary. For a boolean-style
  rule (threshold crossing), confidence = distance from boundary
  normalized by the range, clipped to [0.0, 1.0]. This gives a richer
  signal than just the binary type label.
* 'rule_matched' is a human-readable string that states exactly which
  condition triggered — required for the explainability contract (section 9.2).
* behavioral_score is incorporated if present: if behavioral is 0.0 (meaning
  outputs diverge) with high lexical+structural, we downgrade from
  exact_copy to structural_refactoring.
* All input scores are expected in [0.0, 1.0]; None values are treated as
  absent (use 0.0 for threshold comparisons only when safe, else skip).
"""
from __future__ import annotations

from typing import Any

from app.config import settings

# ──────────────────────────────────────────────────────────────────────────────
# Decision thresholds — adjust here for ablation studies
# ──────────────────────────────────────────────────────────────────────────────

# AI rewrite
AI_REWRITE_THRESHOLD: float = settings.AI_GENERATION_THRESHOLD  # from config (default 0.65)

# Exact copy: both channels must be very high
EXACT_COPY_LEX_MIN: float = 0.92
EXACT_COPY_STRUCT_MIN: float = 0.92

# Variable renaming: shape identical, identifiers changed
RENAME_STRUCT_MIN: float = 0.88
RENAME_LEX_MAX: float = 0.75   # lexical low because identifiers differ

# Structural refactoring: meaningful shape change but same semantic intent
REFACTOR_STRUCT_MIN: float = 0.55
REFACTOR_STRUCT_MAX: float = 0.88
REFACTOR_SEM_MIN: float = 0.60  # semantic confirms same intent
REFACTOR_LEX_MIN: float = 0.45  # OR lexical suggests shared code

# Partial match: any meaningful overlap
PARTIAL_MATCH_MIN: float = 0.30

# Behavioral: if behavioral is very low with high structure, code diverges functionally
BEHAVIORAL_DIVERGE_MAX: float = 0.25  # behavioral ≤ this means outputs differ meaningfully


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _safe(val: float | None, default: float = 0.0) -> float:
    """Return val if not None, else default. For threshold checks only."""
    return float(val) if val is not None else default


def _distance_confidence(value: float, threshold: float, direction: str = "above") -> float:
    """
    Compute a [0.0, 1.0] confidence based on distance from threshold.

    direction='above': value is above threshold — confidence grows with distance above.
    direction='below': value is below threshold — confidence grows with distance below.
    """
    if direction == "above":
        dist = max(0.0, value - threshold)
        span = 1.0 - threshold if threshold < 1.0 else 1.0
    else:
        dist = max(0.0, threshold - value)
        span = threshold if threshold > 0.0 else 1.0
    return min(1.0, dist / span)


# ──────────────────────────────────────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────────────────────────────────────

def detect_transformation(
    scores: dict[str, float | None],
    ai_likelihood: float,
) -> dict[str, Any]:
    """
    Classify the transformation type between two code submissions.

    Parameters
    ----------
    scores : dict
        Keys: 'lexical', 'structural', 'semantic', 'behavioral' (nullable),
        'fusion' (nullable). Values in [0.0, 1.0] or None.
    ai_likelihood : float
        Output of detect_ai_generated() — in [0.0, 1.0].
        CRITICAL: this MUST feed into the classification (not be ignored).
        If >= AI_REWRITE_THRESHOLD, the result is 'likely_ai_rewrite'.

    Returns
    -------
    dict with keys:
      - type: str — one of the 6 category names above
      - confidence: float in [0.0, 1.0]
      - rule_matched: str — human-readable explanation of the triggering rule
      - scores_snapshot: dict — snapshot of inputs used for the decision
        (needed so the UI can display which scores drove the classification)
    """
    lex = _safe(scores.get("lexical"))
    struct = _safe(scores.get("structural"))
    sem = _safe(scores.get("semantic"))
    beh_raw = scores.get("behavioral")   # keep None distinct from 0.0
    beh = _safe(beh_raw)
    fusion = _safe(scores.get("fusion"))

    scores_snapshot = {
        "lexical": lex,
        "structural": struct,
        "semantic": sem,
        "behavioral": beh_raw,  # None preserved in snapshot
        "fusion": fusion,
        "ai_likelihood": ai_likelihood,
    }

    # ── Rule 1: Likely AI Rewrite ──────────────────────────────────────────
    # Check this FIRST — explicitly wires ai_likelihood into classification.
    # Prior build had this siloed. This is the fix.
    if ai_likelihood >= AI_REWRITE_THRESHOLD:
        confidence = _distance_confidence(ai_likelihood, AI_REWRITE_THRESHOLD, "above")
        return {
            "type": "likely_ai_rewrite",
            "confidence": round(confidence, 4),
            "rule_matched": (
                f"AI-generation likelihood ({ai_likelihood:.2f}) ≥ threshold "
                f"({AI_REWRITE_THRESHOLD:.2f}). The code shows patterns consistent "
                f"with AI-assisted generation."
            ),
            "scores_snapshot": scores_snapshot,
        }

    # ── Rule 2: Exact Copy ────────────────────────────────────────────────
    # Both lexical and structural very high.
    # Exception: if behavioral is available AND very low, outputs differ —
    # downgrade to structural_refactoring (logically different despite textual identity).
    if lex >= EXACT_COPY_LEX_MIN and struct >= EXACT_COPY_STRUCT_MIN:
        behavioral_diverges = (beh_raw is not None and beh <= BEHAVIORAL_DIVERGE_MAX)
        if not behavioral_diverges:
            confidence = (
                _distance_confidence(lex, EXACT_COPY_LEX_MIN, "above") * 0.5
                + _distance_confidence(struct, EXACT_COPY_STRUCT_MIN, "above") * 0.5
            )
            return {
                "type": "exact_copy",
                "confidence": round(confidence, 4),
                "rule_matched": (
                    f"Lexical similarity ({lex:.2f}) ≥ {EXACT_COPY_LEX_MIN} AND "
                    f"structural similarity ({struct:.2f}) ≥ {EXACT_COPY_STRUCT_MIN}. "
                    f"Both content and structure are nearly identical."
                ),
                "scores_snapshot": scores_snapshot,
            }
        else:
            # Behavioral divergence detected — fall through to structural_refactoring
            pass

    # ── Rule 3: Variable Renaming ─────────────────────────────────────────
    # Structure essentially identical, but identifiers differ (low lexical).
    if struct >= RENAME_STRUCT_MIN and lex < RENAME_LEX_MAX:
        confidence = (
            _distance_confidence(struct, RENAME_STRUCT_MIN, "above") * 0.6
            + _distance_confidence(lex, RENAME_LEX_MAX, "below") * 0.4
        )
        return {
            "type": "variable_renaming",
            "confidence": round(confidence, 4),
            "rule_matched": (
                f"Structural similarity ({struct:.2f}) ≥ {RENAME_STRUCT_MIN} "
                f"but lexical similarity ({lex:.2f}) < {RENAME_LEX_MAX}. "
                f"Code structure is preserved while identifiers have been changed."
            ),
            "scores_snapshot": scores_snapshot,
        }

    # ── Rule 4: Structural Refactoring ───────────────────────────────────
    # Structure moderately changed, but semantic intent is preserved.
    struct_in_range = REFACTOR_STRUCT_MIN <= struct < REFACTOR_STRUCT_MAX
    semantic_confirms = sem >= REFACTOR_SEM_MIN
    lexical_suggests = lex >= REFACTOR_LEX_MIN
    if struct_in_range and (semantic_confirms or lexical_suggests):
        reason_parts = [
            f"structural similarity ({struct:.2f}) in "
            f"[{REFACTOR_STRUCT_MIN}, {REFACTOR_STRUCT_MAX})"
        ]
        if semantic_confirms:
            reason_parts.append(
                f"semantic similarity ({sem:.2f}) ≥ {REFACTOR_SEM_MIN} "
                f"(same intent preserved)"
            )
        if lexical_suggests:
            reason_parts.append(
                f"lexical overlap ({lex:.2f}) ≥ {REFACTOR_LEX_MIN} "
                f"(shared code fragments)"
            )
        confidence = (
            _distance_confidence(struct, REFACTOR_STRUCT_MIN, "above") * 0.4
            + (
                _distance_confidence(sem, REFACTOR_SEM_MIN, "above") * 0.35
                if semantic_confirms
                else 0.0
            )
            + (
                _distance_confidence(lex, REFACTOR_LEX_MIN, "above") * 0.25
                if lexical_suggests
                else 0.0
            )
        )
        return {
            "type": "structural_refactoring",
            "confidence": round(min(1.0, confidence), 4),
            "rule_matched": ". ".join(reason_parts) + ".",
            "scores_snapshot": scores_snapshot,
        }

    # ── Rule 5: Partial Match ─────────────────────────────────────────────
    # Aggregate fusion score above noise floor.
    if fusion >= PARTIAL_MATCH_MIN:
        confidence = _distance_confidence(fusion, PARTIAL_MATCH_MIN, "above")
        return {
            "type": "partial_match",
            "confidence": round(confidence, 4),
            "rule_matched": (
                f"Fusion similarity ({fusion:.2f}) ≥ {PARTIAL_MATCH_MIN} "
                f"but no specific transformation pattern matched. "
                f"Some overlapping code fragments detected."
            ),
            "scores_snapshot": scores_snapshot,
        }


    # ── Rule 6: Unrelated ─────────────────────────────────────────────────
    # No meaningful similarity found.
    best_score = max(lex, struct, sem, fusion, _safe(beh_raw))
    confidence = _distance_confidence(best_score, PARTIAL_MATCH_MIN, "below")
    return {
        "type": "unrelated",
        "confidence": round(confidence, 4),
        "rule_matched": (
            f"Fusion score ({fusion:.2f}) and signals below {PARTIAL_MATCH_MIN} threshold. "
            f"Highest individual signal: {best_score:.2f}. "
            f"No meaningful overlap detected between the two submissions."
        ),
        "scores_snapshot": scores_snapshot,
    }

