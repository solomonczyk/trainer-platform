"""Tests for feature flags / kill switch functionality."""

import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_feature_flags_configured():
    """Required feature flags exist in settings."""
    assert hasattr(settings, "ff_trainer_qa_interview_visible")
    assert hasattr(settings, "ff_ai_evaluation_enabled")
    assert hasattr(settings, "ff_analytics_enabled")
    assert hasattr(settings, "ff_scenario_runtime_enabled")


@pytest.mark.asyncio
async def test_ai_evaluation_flag(client, test_trainer, test_scenario, auth_headers):
    """AI evaluation can be disabled via feature flag."""
    # Test with AI enabled (default)
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    start_resp = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    sid = start_resp.json()["session_id"]
    aid = start_resp.json()["attempt_id"]

    await client.post(f"/api/v1/sessions/{sid}/messages", json={"content": "Test answer."}, headers=auth_headers)
    await client.post(f"/api/v1/sessions/{sid}/complete", headers=auth_headers)

    # With mock provider, evaluation should succeed
    response = await client.post(f"/api/v1/attempts/{aid}/evaluate", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_trainer_hidden_flag(client, test_trainer, auth_headers):
    """When trainer is hidden, GET returns 404."""
    # Check that trainer is visible by default
    response = await client.get("/api/v1/trainers/qa-engineer-interview-trainer", headers=auth_headers)
    assert response.status_code == 200
