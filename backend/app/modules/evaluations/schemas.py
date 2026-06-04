"""Pydantic schemas for the evaluations module HTTP API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class EvaluateRequest(BaseModel):
    """Payload for triggering evaluation of an attempt."""

    locale: str = Field(default="ru-RU", description="Evaluation locale (e.g. ru-RU, en-US)")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class CriterionResultResponse(BaseModel):
    """Single criterion evaluation result."""

    criterion_id: str
    score: int = Field(ge=0, le=100)
    evidence: str
    comment: str = ""
    improvement: str = ""


class EvaluationResponse(BaseModel):
    """Full evaluation result for an attempt."""

    id: str
    attempt_id: str
    overall_score: int = Field(ge=0, le=100)
    passed: bool
    criteria: list[CriterionResultResponse] = []
    strengths: list[str] = []
    weak_points: list[str] = []
    critical_errors: list[str] = []
    next_recommendation: Optional[dict[str, Any]] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    ai_model_used: Optional[str] = None
    ai_cost_usd: Optional[float] = None
    ai_latency_ms: Optional[int] = None
    validation_status: str = "validated"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EvaluationTriggerResponse(BaseModel):
    """Response returned after triggering an evaluation."""

    evaluation_id: str
    attempt_id: str
    status: str = "evaluating"
    message: str = "Evaluation started"


# ---------------------------------------------------------------------------
# Error response schemas
# ---------------------------------------------------------------------------


class EvaluationErrorResponse(BaseModel):
    """Standard error response for evaluation endpoints."""

    error: str
    detail: str
    attempt_id: Optional[str] = None
