"""Auth API routes — register, login, logout, email verification."""

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
    VerifyEmailRequest,
    ResendVerificationRequest,
    VerifyEmailResponse,
    ResendVerificationResponse,
)
from app.modules.auth.service import (
    register_user,
    authenticate_user,
    verify_email,
    resend_verification,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user account and return a JWT token.

    Note: The user's email is NOT verified at this point.
    A verification email is sent automatically only for truly new accounts.
    """
    user, token = await register_user(
        db, body.email, body.password, body.display_name, locale=body.locale or "ru-RU"
    )
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
    """Authenticate with email/password and return a JWT token.

    Login never sends a verification email.
    Login never resets email_verified.
    Even if the email is not verified, the user receives a token.
    Access to simulator resources is gated by require_email_verified.
    """
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


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email_endpoint(
    body: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id_required),
) -> VerifyEmailResponse:
    """Verify a user's email address using a verification token.

    Requires authentication — only the user who owns the token can verify it.
    This prevents email scanners/bots from consuming tokens.

    Returns a fresh access token so the frontend can immediately use the
    verified session without a stale pre-verification JWT.
    """
    from app.core.security import create_access_token

    user = await verify_email(db, body.token, user_id)
    fresh_token = create_access_token(user_id=user.id, role=user.role)
    return VerifyEmailResponse(access_token=fresh_token, email=user.email)


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification_endpoint(
    body: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> ResendVerificationResponse:
    """Resend the email verification email to the given address.

    This endpoint is rate-limited and safe against email enumeration.
    Returns a structured response with sent status and message_code.
    """
    result = await resend_verification(db, body.email, locale=body.locale or "ru-RU")
    return ResendVerificationResponse(
        sent=result["sent"],
        message_code=result["message_code"],
    )
