"""Tests for progress engine."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import TrainerProgress


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


@pytest.mark.asyncio
async def test_progress_updated_after_evaluation(client, test_trainer, test_scenario, auth_headers, db):
    """Progress is auto-updated after a successful evaluation."""
    # Enroll, start scenario, submit, complete, evaluate
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    start_resp = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    session_id = start_resp.json()["session_id"]
    attempt_id = start_resp.json()["attempt_id"]

    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "A bug report should have: title, steps to reproduce, actual result, expected result, environment, severity, and attachments."},
        headers=auth_headers,
    )
    await client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )

    # Before evaluation, progress should show 0 attempts
    progress_before = await client.get(
        "/api/v1/me/progress/qa-engineer-interview-trainer",
        headers=auth_headers,
    )
    assert progress_before.status_code == 200
    assert progress_before.json()["total_attempts"] == 0

    # Evaluate
    eval_resp = await client.post(
        f"/api/v1/attempts/{attempt_id}/evaluate",
        headers=auth_headers,
    )
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()

    # After evaluation, progress should reflect the attempt
    progress_after = await client.get(
        "/api/v1/me/progress/qa-engineer-interview-trainer",
        headers=auth_headers,
    )
    assert progress_after.status_code == 200
    data = progress_after.json()
    assert data["total_attempts"] >= 1
    assert data["average_score"] > 0
    assert data["average_score"] == pytest.approx(eval_data["overall_score"], abs=1)
    assert data["readiness_status"] in ("started", "developing", "ready", "strong")

    # Verify progress record exists in DB
    result = await db.execute(
        select(TrainerProgress).where(
            TrainerProgress.trainer_product_id == test_trainer.id
        )
    )
    tp = result.scalar_one_or_none()
    assert tp is not None
    assert tp.total_attempts >= 1
    assert tp.completed_scenarios >= (1 if eval_data["passed"] else 0)
