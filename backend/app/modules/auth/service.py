"""Auth business logic — registration, authentication, email verification."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError, ForbiddenError, AppError, NotFoundError
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email import send_email, build_verification_email, normalize_email
from app.db.models import User, UserProfile

from app.modules.auth.repository import (
    create_user,
    get_user_by_email,
    get_user_by_verification_token,
    verify_user_email,
    set_verification_token,
)

# Rate-limiting for resend: minimum seconds between resend attempts
_RESEND_COOLDOWN_SECONDS = 60


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
    locale: str = "ru-RU",
) -> tuple[User, str]:
    """Register a new user, set email_verified=False, send verification email.

    Never creates a duplicate user. If the email already exists:
      - verified: raises ConflictError — user should log in instead.
      - unverified: raises ConflictError — user should check inbox or request resend.
                     Does NOT auto-send a new verification email.
    """
    normalized_email = normalize_email(email)
    existing = await get_user_by_email(db, normalized_email)

    if existing:
        if existing.email_verified:
            raise ConflictError(
                "An account with this email already exists. Please log in."
            )
        # Unverified existing account — do not auto-resend.
        # Tell the user to check their inbox or use the resend endpoint explicitly.
        raise ConflictError(
            "An account with this email already exists but email is not yet verified. "
            "Please check your inbox for the verification email, or request a new one."
        )

    password_hash = hash_password(password)
    user = await create_user(db, normalized_email, password_hash)

    if display_name:
        profile = UserProfile(
            id=secrets.token_hex(16),
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

    # Send initial verification email for truly new accounts only
    subject, text_body, html_body = build_verification_email(
        normalized_email, token, locale=locale
    )
    try:
        await send_email(normalized_email, subject, html_body, text_body)
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
    """Authenticate a user by email/password, return (user, token).

    Login never sends a verification email.
    Login never resets email_verified.
    Login never creates a user.
    The user's verified status is read from the database and returned faithfully.
    """
    normalized_email = normalize_email(email)
    user = await get_user_by_email(db, normalized_email)
    if not user:
        raise UnauthorizedError("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    token = create_access_token(user_id=user.id, role=user.role)
    return user, token


async def verify_email(db: AsyncSession, token: str, owner_user_id: str) -> User:
    """Verify a user's email using a verification token.

    The authenticated user (owner_user_id) must own the token.
    This prevents email scanners/bots from consuming tokens.

    Raises:
        NotFoundError: if the token is invalid.
        ForbiddenError: if the authenticated user does not own the token.
        AppError: if the token has expired.
        AppError: if the token has already been used.
    """
    user = await get_user_by_verification_token(db, token)
    if not user:
        raise NotFoundError("Verification token", token)

    if user.id != owner_user_id:
        raise ForbiddenError("This verification link belongs to a different account.")

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


async def resend_verification(
    db: AsyncSession,
    email: str,
    locale: str = "ru-RU",
) -> dict:
    """Generate a new verification token and re-send the verification email.

    Always returns a safe response to avoid email enumeration.
    Rate-limited: respects a minimum cooldown between resend attempts.

    Returns dict with sent: bool and message_code: str.
    """
    normalized_email = normalize_email(email)
    user = await get_user_by_email(db, normalized_email)

    # Always return a safe response to avoid email enumeration
    if not user:
        return {"sent": False, "message_code": "if_account_exists_email_sent"}

    if user.email_verified:
        return {"sent": False, "message_code": "already_verified"}

    # Rate-limit: check if recently sent
    if _recently_sent(user):
        return {"sent": False, "message_code": "rate_limited_or_recently_sent"}

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.email_verification_token_expire_hours
    )
    await set_verification_token(db, user, token, expires_at)

    subject, text_body, html_body = build_verification_email(
        normalized_email, token, locale=locale
    )
    try:
        await send_email(normalized_email, subject, html_body, text_body)
    except Exception:
        # Email failure is not fatal — user can try again
        pass

    return {"sent": True, "message_code": "verification_email_sent"}


def _recently_sent(user: User) -> bool:
    """Check if a verification email was sent recently (within cooldown period).

    Uses the token expiry reset time as a heuristic. If the token was updated
    within the cooldown window, consider it recently sent.
    """
    if not user.email_verification_token_expires_at:
        return False
    expires = user.email_verification_token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    token_age = datetime.now(timezone.utc) - (
        expires - timedelta(hours=settings.email_verification_token_expire_hours)
    )
    return token_age.total_seconds() < _RESEND_COOLDOWN_SECONDS
