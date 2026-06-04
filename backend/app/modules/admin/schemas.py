"""Pydantic schemas for the admin module."""

from __future__ import annotations

from pydantic import BaseModel


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
