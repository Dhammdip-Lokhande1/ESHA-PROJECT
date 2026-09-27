"""
tests/test_adaptive_trainer.py
==============================
Test suite for adaptive fusion retraining.

Verifies:
  1. Fails gracefully if not enough data.
  2. Fails gracefully if only one class (all confirmed).
  3. Extracts non-negative, normalized weights from LogisticRegression.
  4. Persists the new weights to FusionWeightHistory.
"""
from __future__ import annotations

import json

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Feedback, FusionWeightHistory, Run
from app.fusion.adaptive_trainer import retrain_fusion_weights


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh in-memory SQLite DB for tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_retrain_no_data(db_session):
    result = await retrain_fusion_weights(db_session)
    assert result["status"] == "error"
    assert "No feedback data" in result["message"]


@pytest.mark.asyncio
async def test_retrain_one_class_only(db_session):
    # Add some runs but all are "confirmed"
    for i in range(5):
        run = Run(lexical_score=0.9, structural_score=0.9, semantic_score=0.9, behavioral_score=0.9)
        db_session.add(run)
        await db_session.flush()
        fb = Feedback(run_id=run.id, verdict="confirmed")
        db_session.add(fb)
    await db_session.flush()

    result = await retrain_fusion_weights(db_session)
    assert result["status"] == "error"
    assert "requires both" in result["message"]


@pytest.mark.asyncio
async def test_retrain_insufficient_samples(db_session):
    # One confirmed, one false positive -> 2 samples < 5 minimum
    run1 = Run(lexical_score=0.9, structural_score=0.9, semantic_score=0.9, behavioral_score=0.9)
    run2 = Run(lexical_score=0.1, structural_score=0.1, semantic_score=0.1, behavioral_score=0.1)
    db_session.add_all([run1, run2])
    await db_session.flush()
    fb1 = Feedback(run_id=run1.id, verdict="confirmed")
    fb2 = Feedback(run_id=run2.id, verdict="false_positive")
    db_session.add_all([fb1, fb2])
    await db_session.flush()

    result = await retrain_fusion_weights(db_session)
    assert result["status"] == "error"
    assert "Insufficient data" in result["message"]


@pytest.mark.asyncio
async def test_retrain_success(db_session):
    # Add enough samples
    # Positive examples (high scores)
    for _ in range(5):
        r = Run(lexical_score=0.9, structural_score=0.9, semantic_score=0.9, behavioral_score=0.9)
        db_session.add(r)
        await db_session.flush()
        db_session.add(Feedback(run_id=r.id, verdict="confirmed"))

    # Negative examples (low scores)
    for _ in range(5):
        r = Run(lexical_score=0.1, structural_score=0.1, semantic_score=0.1, behavioral_score=0.1)
        db_session.add(r)
        await db_session.flush()
        db_session.add(Feedback(run_id=r.id, verdict="false_positive"))

    await db_session.flush()

    result = await retrain_fusion_weights(db_session)
    
    assert result["status"] == "success"
    assert "new_weights" in result
    assert result["trained_on_n_samples"] == 10
    
    weights = result["new_weights"]
    assert "lexical" in weights
    assert "structural" in weights
    assert "semantic" in weights
    assert "behavioral" in weights
    
    # Check normalization
    total = sum(weights.values())
    assert pytest.approx(total, 0.001) == 1.0
    
    # Check persistence
    hist_result = await db_session.execute(select(FusionWeightHistory))
    history = hist_result.scalars().all()
    assert len(history) == 1
    stored_weights = json.loads(history[0].weights)
    assert stored_weights == weights
