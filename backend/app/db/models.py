"""
db/models.py — SQLAlchemy 2.0 ORM models.

Tables:
  - runs              : one row per pairwise analysis
  - evidence          : one row per evidence item (evidence MUST be persisted — not just returned in JSON)
  - feedback          : instructor verdicts that drive adaptive fusion retraining
  - fusion_weight_history : audit trail of every adaptive retraining event
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ──────────────────────────────────────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────────────────────────────────────
# users
# ──────────────────────────────────────────────────────────────────────────────
class User(Base):
    """
    User accounts for Authentication and Role-Based Access Control (RBAC).
    Roles: 'user' | 'admin'
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    runs: Mapped[list["Run"]] = relationship("Run", back_populates="user")
    feedback_items: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")


# ──────────────────────────────────────────────────────────────────────────────
# runs
# ──────────────────────────────────────────────────────────────────────────────
class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    file_a_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_b_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    lexical_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    structural_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    behavioral_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fusion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # JSON snapshot of the weights that were active at the time of this run.
    fusion_weights_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    transformation_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transformation_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_generation_likelihood: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="runs")
    evidence_items: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="run", cascade="all, delete-orphan"
    )
    feedback_items: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="run", cascade="all, delete-orphan"
    )


# ──────────────────────────────────────────────────────────────────────────────
# evidence
# ──────────────────────────────────────────────────────────────────────────────
class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dimension: Mapped[str] = mapped_column(String, nullable=False)
    file_ref: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[str] = mapped_column(Text, nullable=False)

    run: Mapped["Run"] = relationship("Run", back_populates="evidence_items")


# ──────────────────────────────────────────────────────────────────────────────
# feedback
# ──────────────────────────────────────────────────────────────────────────────
class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint(
            "verdict IN ('confirmed', 'false_positive')", name="ck_feedback_verdict"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    verdict: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    run: Mapped["Run"] = relationship("Run", back_populates="feedback_items")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="feedback_items")


# ──────────────────────────────────────────────────────────────────────────────
# fusion_weight_history
# ──────────────────────────────────────────────────────────────────────────────
class FusionWeightHistory(Base):
    __tablename__ = "fusion_weight_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weights: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    trained_on_n_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
