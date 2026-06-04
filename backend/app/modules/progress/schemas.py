"""Pydantic schemas for the progress module."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class SkillScoreResponse(BaseModel):
    """Score for a single skill within a trainer's progress."""

    skill_id: str
    skill_name: str
    score: float
    level: str
    attempts_count: int


class ProgressSummaryResponse(BaseModel):
    """Aggregated progress summary for a single trainer."""

    trainer_slug: str
    trainer_name: str
    average_score: float
    completed_scenarios: int
    total_attempts: int
    readiness_status: str
    skill_scores: list[SkillScoreResponse]


class AllProgressResponse(BaseModel):
    """Response wrapping a list of trainer progress summaries."""

    progress_list: list[ProgressSummaryResponse]
