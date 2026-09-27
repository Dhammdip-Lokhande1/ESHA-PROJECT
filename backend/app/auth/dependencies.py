"""
auth/dependencies.py — FastAPI dependencies for Authentication, RBAC, and Ownership.

Provides:
  - get_current_user_optional: Returns User or None (supports backward compatibility)
  - get_current_user: Returns User or raises 401
  - require_role(*roles): Factory returning a dependency that enforces allowed roles or 403
  - verify_run_access: Enforces resource ownership (prevents IDOR)
"""
from __future__ import annotations

from typing import Callable, Optional

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token
from app.db.models import Run, User
from app.db.session import get_db_dependency


async def get_current_user_optional(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db_dependency),
) -> Optional[User]:
    """
    Extract token from 'Authorization: Bearer <token>' header and return User object.
    Returns None if header is missing, token invalid, or user inactive.
    """
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        return user
    return None


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Enforce authenticated user requirement. Raises 401 Unauthorized if not authenticated.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Dependency factory that enforces Role-Based Access Control (RBAC).
    Usage: Depends(require_role("user", "admin"))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden. Access requires one of the following roles: {list(allowed_roles)}.",
            )
        return current_user

    return role_checker


async def verify_run_access(
    run_id: str,
    db: AsyncSession = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Run:
    """
    Verify that the run exists AND the current user is authorized to access it (IDOR Protection).
    Rules:
      - Admins can access any run.
      - Normal Users can access their own runs (run.user_id == current_user.id) or unassigned guest runs.
      - Guests (unauthenticated) can only access unassigned guest runs (run.user_id is None).
    """
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    if current_user is None:
        if run.user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden. Authentication required to access this investigation report.",
            )
        return run

    if current_user.role == "admin":
        return run

    if run.user_id is not None and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. You do not have permission to access this investigation report.",
        )

    return run
