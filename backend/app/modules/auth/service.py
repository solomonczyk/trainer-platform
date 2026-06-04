"""Auth business logic — registration, authentication, token creation."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password, create_access_token
from app.db.models import User, UserProfile

from app.modules.auth.repository import create_user, get_user_by_email


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
) -> tuple[User, str]:
    """Register a new user, optionally create a profile, return (user, token)."""
    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictError(f"User with email {email} already exists")

    password_hash = hash_password(password)
    user = await create_user(db, email, password_hash)

    if display_name:
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            display_name=display_name,
        )
        db.add(profile)
        await db.flush()

    token = create_access_token(user_id=user.id, role=user.role)
    return user, token


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
