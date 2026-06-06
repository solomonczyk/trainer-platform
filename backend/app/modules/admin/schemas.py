"""Pydantic schemas for the admin module."""

from __future__ import annotations
from typing import Any, Optional

from pydantic import BaseModel


class InlineSeedRequest(BaseModel):
    """Optional inline JSON data for seeding on environments without local file access.

    All fields are optional; when provided they override file-based loading.
    """

    trainer_data: Optional[dict[str, Any]] = None
    modules_data: Optional[list[dict[str, Any]]] = None
    activities_data: Optional[list[dict[str, Any]]] = None
    locale_data: Optional[dict[str, Any]] = None
    scenarios_data: Optional[list[dict[str, Any]]] = None
    rubrics_data: Optional[dict[str, Any]] = None


class SeedStatusResponse(BaseModel):
    """Counts of seeded entities across the platform."""

    domains: int
    trainers: int
    scenarios: int
    rubrics: int
    locales: int
    skills: int
    enrollments: int


class SystemHealthResponse(BaseModel):
    """System health summary."""

    status: str
    database: str
    modules: dict


class AdminAnalyticsSanityResponse(BaseModel):
    """Analytics event sanity check."""

    total_events: int
    events_by_type: list[dict]
