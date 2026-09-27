"""
api/admin_routes.py — Admin User Management API endpoints.

Requires 'admin' role (require_role("admin")).

Endpoints:
  - GET   /api/v1/admin/users          : List all user accounts
  - PATCH /api/v1/admin/users/{user_id}: Update user role or active status
"""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db.models import User
from app.db.session import get_db_dependency

router = APIRouter(prefix="/admin", tags=["Admin User Management"])


class UpdateUserRequest(BaseModel):
    role: Optional[Literal["user", "admin"]] = None
    is_active: Optional[bool] = None


class UserDetailResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None


@router.get(
    "/users",
    response_model=list[UserDetailResponse],
    summary="List all user accounts (Admin only)",
)
async def list_users(
    db: AsyncSession = Depends(get_db_dependency),
    _: User = Depends(require_role("admin")),
) -> list[UserDetailResponse]:
    """Returns a list of all registered users."""
    stmt = select(User).order_by(User.created_at.desc())
    results = await db.execute(stmt)
    users = results.scalars().all()

    return [
        UserDetailResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            is_active=bool(u.is_active),
            created_at=u.created_at.isoformat() if u.created_at else None,
        )
        for u in users
    ]


@router.patch(
    "/users/{user_id}",
    response_model=UserDetailResponse,
    summary="Update a user's role or status (Admin only)",
)
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    db: AsyncSession = Depends(get_db_dependency),
    admin_user: User = Depends(require_role("admin")),
) -> UserDetailResponse:
    """Updates role or active state of a user."""
    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found.",
        )

    # Protect self-demotion or self-deactivation of primary admin
    if user.id == admin_user.id:
        if body.role and body.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot demote their own account.",
            )
        if body.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot deactivate their own account.",
            )

    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = 1 if body.is_active else 0

    await db.commit()

    return UserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=bool(user.is_active),
        created_at=user.created_at.isoformat() if user.created_at else None,
    )
