"""Tests for progress engine."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_progress_after_enrollment(client, test_trainer, auth_headers):
    """Progress exists after enrollment."""
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/me/progress",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "progress_list" in data


@pytest.mark.asyncio
async def test_trainer_specific_progress(client, test_trainer, auth_headers):
    """GET /api/v1/me/progress/{trainer_slug} returns trainer progress."""
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/me/progress/qa-engineer-interview-trainer",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_score" in data
    assert "readiness_status" in data
    assert data["readiness_status"] in ("started", "developing", "ready", "strong")


@pytest.mark.asyncio
async def test_progress_requires_auth(client, test_trainer):
    """Progress endpoints require authentication."""
    response = await client.get("/api/v1/me/progress")
    assert response.status_code == 401

    response = await client.get("/api/v1/me/progress/qa-engineer-interview-trainer")
    assert response.status_code == 401
