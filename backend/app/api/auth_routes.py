"""
api/auth_routes.py — Authentication API endpoints.

Endpoints:
  - POST /api/v1/auth/register : Public student account registration
  - POST /api/v1/auth/login    : Authenticate username/email & password -> JWT
  - GET  /api/v1/auth/me       : Get current authenticated user profile
  - POST /api/v1/auth/logout   : Logout confirmation
"""
from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.rate_limiter import rate_limit
from app.auth.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.session import get_db_dependency

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ──────────────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Plaintext password")


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool | int
    created_at: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign Up a new user account",
    dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60, key_prefix="register"))],
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db_dependency),
) -> UserResponse:
    """
    Public user sign up.
    Enforces minimum password strength and restricts public registration role strictly to 'user'
    (prevents privilege escalation attacks).
    """
    # 1. Sanitize username
    clean_username = body.username.strip().lower()
    if not re.match(r"^[a-z0-9_-]+$", clean_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username may only contain letters, numbers, underscores, and hyphens.",
        )

    # 2. Check for duplicate username or email
    stmt = select(User).where((User.username == clean_username) | (User.email == body.email.lower()))
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        if existing.username == clean_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{clean_username}' is already taken.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 3. Create user account (strictly forced role='user')
    user = User(
        username=clean_username,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        role="user",
        is_active=1,
    )
    db.add(user)
    await db.flush()

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=bool(user.is_active),
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate credentials and return JWT token",
    dependencies=[Depends(rate_limit(max_requests=15, window_seconds=60, key_prefix="login"))],
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db_dependency),
) -> LoginResponse:
    """
    Authenticate user via username or email + password.
    Returns JWT access token.
    """
    login_str = body.username.strip().lower()

    stmt = select(User).where((User.username == login_str) | (User.email == login_str))
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact an administrator.",
        )

    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role}
    )

    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=bool(user.is_active),
        created_at=user.created_at.isoformat() if user.created_at else None,
    )

    return LoginResponse(access_token=access_token, token_type="bearer", user=user_resp)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Returns currently authenticated user profile."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=bool(current_user.is_active),
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )


@router.post(
    "/logout",
    summary="Logout confirmation endpoint",
)
async def logout() -> dict:
    """Returns confirmation of logout."""
    return {"status": "ok", "message": "Successfully logged out."}
