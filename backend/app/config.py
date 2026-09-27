"""
config.py — Centralized configuration for EHSA backend.
All tunable knobs live here. Import from this module; never hardcode in routes or modules.
"""
from __future__ import annotations

import os
from pydantic_settings import BaseSettings


from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
_db_file = (_project_root / "ehsa.db").as_posix()


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # Database                                                             #
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_db_file}"

    # ------------------------------------------------------------------ #
    # Semantic model                                                       #
    # ------------------------------------------------------------------ #
    # Primary (eval):   microsoft/graphcodebert-base
    # Lighter (deploy): microsoft/unixcoder-base
    MODEL_NAME: str = "microsoft/unixcoder-base"

    # ------------------------------------------------------------------ #
    # File limits                                                          #
    # ------------------------------------------------------------------ #
    MAX_FILE_SIZE_BYTES: int = 1_048_576  # 1 MB — enforced in Pydantic validator
    PBKDF2_ITERATIONS: int = 600_000      # Env-configurable PBKDF2 iterations

    # ------------------------------------------------------------------ #
    # Behavioral sandbox                                                   #
    # ------------------------------------------------------------------ #
    BEHAVIORAL_TIMEOUT_SECONDS: float = 2.0
    # Max memory for sandboxed subprocess (bytes); None → no limit applied
    BEHAVIORAL_MAX_MEMORY_BYTES: int | None = 128 * 1024 * 1024  # 128 MB

    # ------------------------------------------------------------------ #
    # Default fusion weights (fixed-weight mode)                           #
    # Favors semantic (0.35) and structural (0.25); behavioral lower       #
    # because it may be absent. Documented starting point — adaptive      #
    # trainer will override once feedback accumulates.                     #
    # ------------------------------------------------------------------ #
    FUSION_WEIGHTS: dict[str, float] = {
        "lexical": 0.20,
        "structural": 0.25,
        "semantic": 0.35,
        "behavioral": 0.20,
    }

    # Minimum samples needed before adaptive retraining is allowed
    ADAPTIVE_MIN_SAMPLES: int = 10

    # ------------------------------------------------------------------ #
    # CORS                                                                 #
    # ------------------------------------------------------------------ #
    # Comma-separated list of allowed origins. Override via env var.
    # "http://localhost:3000" for local dev; replace with actual Vercel
    # URL in production — never use "*" in production.
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ------------------------------------------------------------------ #
    # AI-generation detector thresholds                                    #
    # ------------------------------------------------------------------ #
    # Score above this → 'likely_ai_rewrite' transformation type
    AI_GENERATION_THRESHOLD: float = 0.65

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
