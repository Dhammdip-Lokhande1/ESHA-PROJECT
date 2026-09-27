"""
fusion/fusion_engine.py
========================
Fixed-weight and adaptive-weight fusion of similarity signals.

Public API (section 8.7 of INSTRUCTIONS.md):

    fuse(scores: dict, weights: dict | None = None) -> tuple[float, dict]

    scores = {lexical, structural, semantic, behavioral (nullable)}
    weights = None → load CURRENT weights from config/DB
    Returns (fused_score, weight_metadata) where weight_metadata states:
      - which weights were used
      - when they were last updated (None if using defaults)

Non-Negotiable Rule 5: adaptive fusion must be explainable.
The system MUST be able to state its current weights and when they were
last updated. weight_metadata satisfies this requirement.

Algorithm
---------
Weighted average over available (non-None) signals.
If behavioral_score is None (signal absent, not "zero behavior match"),
it is EXCLUDED from the fusion rather than dragging the score down.
The weights of the remaining signals are RENORMALIZED to sum to 1.0.
This is the correct behavior: None ≠ 0.0 — it means "not computed."

The weight_metadata in the response always discloses:
  - effective_weights: the normalized weights actually used (behavioral
    excluded if None)
  - behavioral_excluded: bool — transparent about what happened
  - source: "config_default" | "adaptive_trained"
  - last_updated: timestamp | None
"""
from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Weight loading
# ──────────────────────────────────────────────────────────────────────────────

def _load_current_weights(db_session=None) -> tuple[dict[str, float], str, str | None]:
    """
    Load the current fusion weights.

    Priority:
      1. If a DB session is provided, check FusionWeightHistory for the most
         recent trained weights.
      2. Fall back to settings.FUSION_WEIGHTS (config default).

    Returns
    -------
    (weights_dict, source, last_updated_iso)
      - source: "adaptive_trained" | "config_default"
      - last_updated_iso: ISO timestamp string or None
    """
    if db_session is not None:
        try:
            # Import here to avoid circular dependency at module load time
            from app.db.models import FusionWeightHistory  # noqa: PLC0415
            from sqlalchemy import select  # noqa: PLC0415

            # Synchronous query — this function may be called from sync context
            # For async routes, pass weights explicitly instead of db_session
            latest = db_session.execute(
                select(FusionWeightHistory)
                .order_by(FusionWeightHistory.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if latest is not None:
                weights = json.loads(latest.weights)
                return (
                    weights,
                    "adaptive_trained",
                    latest.created_at.isoformat(),
                )
        except Exception as exc:
            logger.warning(f"Failed to load adaptive weights from DB session (sync), falling back to config default: {exc}")

    return settings.FUSION_WEIGHTS.copy(), "config_default", None


async def async_load_current_weights(db_session) -> tuple[dict[str, float], str, str | None]:
    """
    Load the current fusion weights asynchronously.
    """
    if db_session is not None:
        try:
            from app.db.models import FusionWeightHistory  # noqa: PLC0415
            from sqlalchemy import select  # noqa: PLC0415

            result = await db_session.execute(
                select(FusionWeightHistory)
                .order_by(FusionWeightHistory.created_at.desc())
                .limit(1)
            )
            latest = result.scalar_one_or_none()

            if latest is not None:
                weights = json.loads(latest.weights)
                return (
                    weights,
                    "adaptive_trained",
                    latest.created_at.isoformat(),
                )
        except Exception as exc:
            logger.warning(f"Failed to load adaptive weights from DB session (async), falling back to config default: {exc}")

    return settings.FUSION_WEIGHTS.copy(), "config_default", None


# ──────────────────────────────────────────────────────────────────────────────
# Core fusion
# ──────────────────────────────────────────────────────────────────────────────

def fuse(
    scores: dict[str, float | None],
    weights: dict[str, float] | None = None,
    source: str | None = None,
    last_updated: str | None = None,
    db_session=None,
) -> tuple[float, dict[str, Any]]:
    """
    Fuse similarity scores into a single weighted score.

    Parameters
    ----------
    scores : dict
        Keys: 'lexical', 'structural', 'semantic', 'behavioral' (nullable).
        Any value that is None is treated as "signal absent" and excluded
        from the weighted average (weights are renormalized).
    weights : dict | None
        Explicit weights to use. If None, loaded from config/DB.
    source : str | None
        Optional source override (e.g. 'adaptive_trained').
    last_updated : str | None
        Optional last updated timestamp.
    db_session : optional
        SQLAlchemy session — used to check for adaptive weights. Pass None
        if calling from an async context (pass weights explicitly instead).

    Returns
    -------
    fused_score : float
        Weighted average in [0.0, 1.0].
    weight_metadata : dict
        {
          "weights_requested": original weights dict or "loaded_from_config/db",
          "effective_weights": normalized weights actually used,
          "behavioral_excluded": bool,
          "source": "config_default" | "adaptive_trained" | "explicit",
          "last_updated": ISO timestamp | None,
          "signals_used": list of signal names included in the fusion
        }
        Required by Non-Negotiable Rule 5.
    """
    # ── Load weights ───────────────────────────────────────────────────────
    if weights is not None:
        base_weights = dict(weights)
        source = source if source is not None else "explicit"
        last_updated = last_updated
    else:
        base_weights, source, last_updated = _load_current_weights(db_session)


    # ── Determine which signals are available ──────────────────────────────
    signal_keys = ["lexical", "structural", "semantic", "behavioral"]
    available: dict[str, float] = {}
    excluded: list[str] = []

    for key in signal_keys:
        val = scores.get(key)
        if val is not None:
            available[key] = float(val)
        else:
            excluded.append(key)

    # ── Handle degenerate cases ────────────────────────────────────────────
    if not available:
        # No signals at all — return 0 with full transparency
        return 0.0, {
            "weights_requested": base_weights,
            "effective_weights": {},
            "behavioral_excluded": "behavioral" in excluded,
            "excluded_signals": excluded,
            "signals_used": [],
            "source": source,
            "last_updated": last_updated,
            "note": "No signals were available — fused score is 0.0.",
        }

    # ── Renormalize weights to available signals ───────────────────────────
    raw_total = sum(base_weights.get(k, 0.0) for k in available)
    if raw_total <= 0:
        # Equal weights fallback
        effective_weights = {k: 1.0 / len(available) for k in available}
    else:
        effective_weights = {
            k: base_weights.get(k, 0.0) / raw_total for k in available
        }

    # ── Weighted average ───────────────────────────────────────────────────
    fused_score = sum(
        available[k] * effective_weights[k] for k in available
    )
    fused_score = round(max(0.0, min(1.0, fused_score)), 6)

    weight_metadata: dict[str, Any] = {
        "weights_requested": base_weights,
        "effective_weights": effective_weights,
        "behavioral_excluded": "behavioral" in excluded,
        "excluded_signals": excluded,
        "signals_used": list(available.keys()),
        "source": source,
        "last_updated": last_updated,
    }

    if excluded:
        weight_metadata["note"] = (
            f"Signals {excluded} were absent (None) and excluded from fusion. "
            f"Remaining weights were renormalized to sum to 1.0. "
            f"None ≠ 0.0 — excluded signals were not computed, not confirmed different."
        )

    return fused_score, weight_metadata
