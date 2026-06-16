"""User business logic — profile retrieval and updates."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.users.repository import (
    get_user_by_id,
    get_profile_by_user_id,
    create_profile,
    update_profile,
)


async def get_user_profile(db: AsyncSession, user_id: str) -> dict:
    """Return the combined user + profile dict for the given user."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    profile = await get_profile_by_user_id(db, user_id)

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "display_name": profile.display_name if profile else None,
        "preferred_locale": profile.preferred_locale if profile else "ru-RU",
        "email_verified": user.email_verified,
    }


async def update_user_profile(db: AsyncSession, user_id: str, data: dict) -> dict:
    """Update profile fields (create profile if missing) and return the result."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    profile = await get_profile_by_user_id(db, user_id)

    if profile:
        profile = await update_profile(db, profile, data)
    else:
        profile = await create_profile(db, user_id, data)

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "display_name": profile.display_name,
        "preferred_locale": profile.preferred_locale,
    }
