"""Auth business logic — registration, authentication, email verification."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError, AppError, NotFoundError
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email import send_email, build_verification_email
from app.db.models import User, UserProfile

from app.modules.auth.repository import (
    create_user,
    get_user_by_email,
    get_user_by_verification_token,
    verify_user_email,
    set_verification_token,
)


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
) -> tuple[User, str]:
    """Register a new user, set email_verified=False, send verification email, return (user, token)."""
    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictError(f"User with email {email} already exists")

    password_hash = hash_password(password)
    user = await create_user(db, email, password_hash)

    # Email defaults to email_verified=False from model default

    if display_name:
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            display_name=display_name,
        )
        db.add(profile)
        await db.flush()

    # Generate verification token and send email
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.email_verification_token_expire_hours
    )
    await set_verification_token(db, user, token, expires_at)

    subject, text_body, html_body = build_verification_email(email, token)
    try:
        await send_email(email, subject, html_body, text_body)
    except Exception:
        # If email fails, still create the user — they can request resend
        pass

    token_jwt = create_access_token(user_id=user.id, role=user.role)
    return user, token_jwt


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> tuple[User, str]:
    """Authenticate a user by email/password, return (user, token)."""
    user = await get_user_by_email(db, email)
    if not user:
        raise UnauthorizedError("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    token = create_access_token(user_id=user.id, role=user.role)
    return user, token


async def verify_email(db: AsyncSession, token: str) -> User:
    """Verify a user's email using a verification token.

    Raises:
        NotFoundError: if the token is invalid.
        AppError: if the token has expired.
        AppError: if the token has already been used.
    """
    user = await get_user_by_verification_token(db, token)
    if not user:
        raise NotFoundError("Verification token", token)

    if user.email_verified:
        # Token already consumed
        raise AppError(
            code="TOKEN_ALREADY_USED",
            message="This verification link has already been used. Please log in.",
            status_code=400,
        )

    if user.email_verification_token_expires_at:
        expires = user.email_verification_token_expires_at
        # SQLite stores as naive; make aware for comparison
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            raise AppError(
                code="TOKEN_EXPIRED",
                message="Verification token has expired. Request a new verification email.",
                status_code=400,
            )

    await verify_user_email(db, user)
    return user


async def resend_verification(db: AsyncSession, email: str) -> User:
    """Generate a new verification token and re-send the verification email.

    Raises:
        NotFoundError: if the email is not registered.
        AppError: if the email is already verified.
    """
    user = await get_user_by_email(db, email)
    if not user:
        raise NotFoundError("User", email)

    if user.email_verified:
        raise AppError(
            code="ALREADY_VERIFIED",
            message="Email is already verified. Please log in.",
            status_code=400,
        )

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.email_verification_token_expire_hours
    )
    await set_verification_token(db, user, token, expires_at)

    subject, text_body, html_body = build_verification_email(email, token)
    await send_email(email, subject, html_body, text_body)

    return user
