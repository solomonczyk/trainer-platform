"""Pydantic schemas for scenario runtime endpoints."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class StartScenarioResponse(BaseModel):
    """Response returned when a user starts a scenario."""

    session_id: str
    attempt_id: str
    scenario: dict[str, Any]
    status: str


class SubmitMessageRequest(BaseModel):
    """Request body for submitting a user answer message."""

    content: str


class SubmitMessageResponse(BaseModel):
    """Response returned after a message is saved."""

    message_id: str
    status: str


class CompleteSessionResponse(BaseModel):
    """Response returned after an attempt is marked complete."""

    attempt_id: str
    status: str
    message: str
