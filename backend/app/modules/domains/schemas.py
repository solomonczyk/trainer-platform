"""Pydantic schemas for the Domains module."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TrainerSummaryResponse(BaseModel):
    """Minimal trainer representation used in domain detail responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    trainer_product_id: str
    slug: str
    name: str
    description: str | None
    product_type: str


class DomainResponse(BaseModel):
    """Domain listing item with trainer count."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    description: str | None
    icon: str | None
    sort_order: int
    trainer_count: int


class DomainDetailResponse(BaseModel):
    """Domain detail including its published trainers."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    description: str | None
    icon: str | None
    trainers: list[TrainerSummaryResponse]
