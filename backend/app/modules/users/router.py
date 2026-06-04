"""User API routes — profile retrieval and updates."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id_required
from app.db.session import get_db

from app.modules.users.schemas import UserProfileResponse, UpdateProfileRequest
from app.modules.users.service import get_user_profile, update_user_profile

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id_required),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Return the current authenticated user's profile."""
    profile_data = await get_user_profile(db, user_id)
    return UserProfileResponse(**profile_data)


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    body: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id_required),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update the current user's profile (display_name, preferred_locale)."""
    data = body.model_dump(exclude_unset=True)
    profile_data = await update_user_profile(db, user_id, data)
    return UserProfileResponse(**profile_data)
