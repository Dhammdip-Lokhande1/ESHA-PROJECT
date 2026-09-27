"""
db/session.py — SQLAlchemy 2.0 async session factory.

Usage in route handlers:
    async with get_db() as session:
        ...

The DATABASE_URL env var switches between SQLite (local) and Postgres
(deployed) without code changes — same ORM queries work for both.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.models import Base

# ──────────────────────────────────────────────────────────────────────────────
# Engine — created once at import time
# ──────────────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # Set True for SQL debug logging
    future=True,
    # SQLite-specific: must allow same connection in different async contexts
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ──────────────────────────────────────────────────────────────────────────────
# Table creation
# ──────────────────────────────────────────────────────────────────────────────
async def create_tables() -> None:
    """Create all tables if they don't already exist and apply missing migrations."""
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migrate existing SQLite databases if user_id column is missing or roles need migration
        if "sqlite" in settings.DATABASE_URL:
            try:
                await conn.execute(text("ALTER TABLE runs ADD COLUMN user_id VARCHAR REFERENCES users(id);"))
            except Exception:
                pass  # Column already exists
            try:
                await conn.execute(text("ALTER TABLE feedback ADD COLUMN user_id VARCHAR REFERENCES users(id);"))
            except Exception:
                pass  # Column already exists
            try:
                await conn.execute(text("UPDATE users SET role = 'user' WHERE role IN ('instructor', 'student');"))
            except Exception:
                pass  # Table or roles already migrated



# ──────────────────────────────────────────────────────────────────────────────
# Session dependency
# ──────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a DB session and handles commit/rollback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Depends-compatible async generator for DB sessions.

    Usage in route handlers:
        async def my_route(db: AsyncSession = Depends(get_db_dependency)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

