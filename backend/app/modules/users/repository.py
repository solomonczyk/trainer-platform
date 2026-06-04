"""User database operations — CRUD for User and UserProfile records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.models import User, UserProfile


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Look up a user by their primary key."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_profile_by_user_id(db: AsyncSession, user_id: str) -> UserProfile | None:
    """Look up a user profile by the user's ID (one-to-one)."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def create_profile(db: AsyncSession, user_id: str, data: dict) -> UserProfile:
    """Create a new profile for a user and return it."""
    profile = UserProfile(
        id=generate_uuid(),
        user_id=user_id,
        display_name=data.get("display_name"),
        preferred_locale=data.get("preferred_locale", "ru-RU"),
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


async def update_profile(
    db: AsyncSession,
    profile: UserProfile,
    data: dict,
) -> UserProfile:
    """Update profile fields in-place and return the refreshed object."""
    if "display_name" in data:
        profile.display_name = data["display_name"]
    if "preferred_locale" in data:
        profile.preferred_locale = data["preferred_locale"]
    await db.flush()
    await db.refresh(profile)
    return profile
