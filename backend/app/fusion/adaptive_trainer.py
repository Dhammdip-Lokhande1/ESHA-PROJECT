"""
fusion/adaptive_trainer.py
==========================
Adaptive retraining of fusion weights based on instructor feedback.

Extracts features (lexical, structural, semantic, behavioral scores) from runs
that have associated feedback ('confirmed' or 'false_positive').
Trains a Logistic Regression model to find optimal feature coefficients.
Normalizes the coefficients into sum-to-1 weights, and saves to the DB.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Lazy load sklearn since retraining happens rarely
try:
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from app.db.models import Feedback, FusionWeightHistory, Run


async def retrain_fusion_weights(db_session: AsyncSession) -> dict[str, Any]:
    """
    Retrain fusion weights based on historical feedback (Async).

    Queries all runs with feedback.
    Features: lexical_score, structural_score, semantic_score, behavioral_score (filled with 0.0 if None)
    Labels: 1 if verdict == 'confirmed' else 0

    If there is not enough variance (e.g. all confirmed or all false_positive),
    or fewer than a minimum number of samples, returns an error dict.

    Returns
    -------
    dict:
        {
            "status": "success" | "error",
            "new_weights": dict (if success),
            "trained_on_n_samples": int (if success),
            "timestamp": str (if success),
            "message": str (if error)
        }
    """
    if not HAS_SKLEARN:
        return {
            "status": "error",
            "message": "scikit-learn is not installed. Cannot retrain adaptive weights."
        }

    # 1. Fetch data
    stmt = (
        select(Run, Feedback)
        .join(Feedback, Feedback.run_id == Run.id)
    )
    result_proxy = await db_session.execute(stmt)
    results = result_proxy.all()

    if not results:
        return {
            "status": "error",
            "message": "No feedback data available for training."
        }

    X = []
    y = []

    for run, feedback in results:
        # Impute missing values with 0.0
        features = [
            run.lexical_score if run.lexical_score is not None else 0.0,
            run.structural_score if run.structural_score is not None else 0.0,
            run.semantic_score if run.semantic_score is not None else 0.0,
            run.behavioral_score if run.behavioral_score is not None else 0.0,
        ]
        label = 1 if feedback.verdict == "confirmed" else 0
        
        X.append(features)
        y.append(label)

    X_np = np.array(X)
    y_np = np.array(y)

    # Need at least one of each class to train logistic regression
    if len(np.unique(y_np)) < 2:
        return {
            "status": "error",
            "message": "Training requires both 'confirmed' and 'false_positive' samples."
        }
        
    # Optional: require a minimum number of samples (e.g. 5) to avoid wild swings
    if len(y_np) < 5:
        return {
            "status": "error",
            "message": f"Insufficient data: {len(y_np)} samples. Need at least 5."
        }

    # 2. Train model
    # Use positive=True to force non-negative weights if available in newer sklearn,
    # otherwise clip negative coefficients to a small positive epsilon before normalizing.
    # We want standard normalization, no intercept helps interpretability.
    clf = LogisticRegression(fit_intercept=False, penalty="l2", C=1.0)
    clf.fit(X_np, y_np)

    coefs = clf.coef_[0]
    
    # Clip negative coefficients to a small epsilon (e.g. 0.01) so they aren't zeroed out completely
    # but don't negatively subtract from the score.
    coefs = np.clip(coefs, a_min=0.01, a_max=None)
    
    # Normalize to sum to 1.0
    weights_normalized = coefs / np.sum(coefs)

    new_weights = {
        "lexical": float(weights_normalized[0]),
        "structural": float(weights_normalized[1]),
        "semantic": float(weights_normalized[2]),
        "behavioral": float(weights_normalized[3]),
    }

    # 3. Persist to DB
    history_entry = FusionWeightHistory(
        weights=json.dumps(new_weights),
        trained_on_n_samples=len(y_np),
    )
    db_session.add(history_entry)
    await db_session.flush()

    return {
        "status": "success",
        "new_weights": new_weights,
        "trained_on_n_samples": len(y_np),
        "timestamp": history_entry.created_at.isoformat() if history_entry.created_at else datetime.now(timezone.utc).isoformat()
    }
