"""Auth API routes — register, login, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id_required
from app.db.session import get_db

from app.modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import register_user, authenticate_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user account and return a JWT token."""
    user, token = await register_user(db, body.email, body.password, body.display_name)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email/password and return a JWT token."""
    user, token = await authenticate_user(db, body.email, body.password)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user_id_required),
) -> dict:
    """Logout placeholder — invalidates the current session."""
    return {"message": "Logged out successfully"}
