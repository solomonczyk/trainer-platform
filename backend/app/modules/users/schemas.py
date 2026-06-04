"""User-related Pydantic schemas for profile endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    """Full user profile returned to the client."""

    id: str
    email: str
    role: str
    display_name: Optional[str] = None
    preferred_locale: str = "ru-RU"
    is_active: bool

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    """Request body for updating user profile fields."""

    display_name: Optional[str] = Field(None, max_length=255, description="Display name")
    preferred_locale: Optional[str] = Field(None, max_length=10, description="Preferred locale (e.g. ru-RU, en-US)")
