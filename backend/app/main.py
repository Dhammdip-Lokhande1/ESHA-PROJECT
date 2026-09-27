"""
main.py — FastAPI application factory.

Responsibilities:
  - Create the FastAPI app with lifespan (DB table creation on startup).
  - Mount CORS middleware.
  - Include the API router.
  - Expose GET /health for uptime checks.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.session import create_tables


async def _bootstrap_admin() -> None:
    """Ensure at least one admin user exists in DB on startup."""
    from app.auth.security import hash_password
    from app.db.models import User
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.role == "admin")
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            admin_user = User(
                username=getattr(settings, "INITIAL_ADMIN_USERNAME", "admin"),
                email=getattr(settings, "INITIAL_ADMIN_EMAIL", "admin@ehsa.local"),
                password_hash=hash_password(
                    getattr(settings, "INITIAL_ADMIN_PASSWORD", "AdminSecretPass123!")
                ),
                role="admin",
                is_active=1,
            )
            session.add(admin_user)
            await session.commit()


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan — runs once on startup and shutdown
# ──────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create DB tables, bootstrap admin, and pre-warm semantic model on startup."""
    import asyncio
    from app.similarity.semantic import _load_model

    await create_tables()
    await _bootstrap_admin()
    # Pre-warm model in background thread so first request is instant
    asyncio.create_task(asyncio.to_thread(_load_model))
    yield
    # Shutdown: nothing to clean up currently; add connection-pool teardown here
    # if switching from SQLite to async Postgres.


# ──────────────────────────────────────────────────────────────────────────────
# App factory
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EHSA — Explainable Hybrid Similarity Analyzer",
    description=(
        "Evidence-first Python source-code similarity investigation tool. "
        "Every score carries traceable evidence. Fusion weights adapt from "
        "real analysis feedback. Zero paid APIs."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — restricted to configured origins (section 12 security requirement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Global Exception Handling & Security Error Suppression
# ──────────────────────────────────────────────────────────────────────────────
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ehsa")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Sanitize internal server errors to prevent exposing stack traces,
    database errors, or internal filesystem paths to clients.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    logger.error(f"Unhandled internal server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


# ──────────────────────────────────────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────────────────────────────────────
from app.api.auth_routes import router as auth_router  # noqa: E402
from app.api.admin_routes import router as admin_router  # noqa: E402
from app.api.routes import router as api_router  # noqa: E402

app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")


# ──────────────────────────────────────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Returns {status: 'ok'} — used by uptime monitors and Docker health checks."""
    return {"status": "ok"}
