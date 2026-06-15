"""Auth database operations — CRUD for User records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.models import User


async def create_user(db: AsyncSession, email: str, password_hash: str) -> User:
    """Insert a new user and return it."""
    user = User(
        id=generate_uuid(),
        email=email,
        password_hash=password_hash,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Look up a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Look up a user by their primary key."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_verification_token(db: AsyncSession, token: str) -> User | None:
    """Look up a user by their email verification token."""
    result = await db.execute(
        select(User).where(User.email_verification_token == token)
    )
    return result.scalar_one_or_none()


async def verify_user_email(db: AsyncSession, user: User) -> None:
    """Mark a user's email as verified.

    Note: The verification token is kept so that reused-token detection
    (TOKEN_ALREADY_USED) can still look up the user by token.
    """
    user.email_verified = True
    user.email_verification_token_expires_at = None
    await db.flush()


async def set_verification_token(
    db: AsyncSession,
    user: User,
    token: str,
    expires_at: datetime,
) -> None:
    """Set the email verification token and its expiry on a user."""
    user.email_verification_token = token
    user.email_verification_token_expires_at = expires_at
    await db.flush()
