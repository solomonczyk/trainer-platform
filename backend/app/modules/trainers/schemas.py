"""Pydantic schemas for the Trainers module."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TrainerDetailResponse(BaseModel):
    """Full trainer detail including scenario count and enrollment status."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    trainer_product_id: str
    slug: str
    name: str
    description: str | None
    product_type: str
    target_audience: list | None
    supported_locales: list | None
    default_locale: str
    status: str
    scenario_count: int
    is_enrolled: bool


class EnrollResponse(BaseModel):
    """Response returned after enrolling in a trainer."""

    enrollment_id: str
    status: str
    message: str
