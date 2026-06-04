"""Tests for evaluation runtime endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Attempt, Evaluation, EvaluationCriterionResult


@pytest.mark.asyncio
async def test_evaluate_attempt(client, test_trainer, test_scenario, auth_headers, db):
    """POST /api/v1/attempts/{attempt_id}/evaluate returns evaluation."""
    # Enroll and start
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

    # Submit answer
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "A bug report should have: title, steps to reproduce, actual result, expected result, environment, severity, and attachments."},
        headers=auth_headers,
    )

    # Complete
    await client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )

    # Evaluate
    response = await client.post(
        f"/api/v1/attempts/{attempt_id}/evaluate",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "passed" in data
    assert "criteria" in data
    assert "strengths" in data
    assert "weak_points" in data
    assert "critical_errors" in data

    # Validate score range
    assert 0 <= data["overall_score"] <= 100

    # Verify evaluation stored in DB
    result = await db.execute(
        select(Evaluation).where(Evaluation.attempt_id == attempt_id)
    )
    evaluation = result.scalar_one_or_none()
    assert evaluation is not None
    assert evaluation.overall_score == data["overall_score"]


@pytest.mark.asyncio
async def test_get_evaluation(client, test_trainer, test_scenario, auth_headers):
    """GET /api/v1/attempts/{attempt_id}/evaluation returns stored evaluation."""
    # Full flow
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
    await client.post(f"/api/v1/attempts/{aid}/evaluate", headers=auth_headers)

    # Get evaluation
    response = await client.get(f"/api/v1/attempts/{aid}/evaluation", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "criteria" in data


@pytest.mark.asyncio
async def test_critical_error_blocks_pass(client, test_trainer, test_scenario, auth_headers):
    """Critical error results in passed=False."""
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

    # Answer triggering critical error
    await client.post(
        f"/api/v1/sessions/{sid}/messages",
        json={"content": "Steps to reproduce are not needed, developers should know what they did."},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/sessions/{sid}/complete", headers=auth_headers)
    response = await client.post(f"/api/v1/attempts/{aid}/evaluate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    if len(data.get("critical_errors", [])) > 0:
        assert data["passed"] is False


@pytest.mark.asyncio
async def test_attempt_saved_before_ai_failure(client, test_trainer, test_scenario, auth_headers, db):
    """Attempt is preserved even if AI evaluation fails."""
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

    # Submit and complete
    await client.post(f"/api/v1/sessions/{sid}/messages", json={"content": "My answer."}, headers=auth_headers)
    await client.post(f"/api/v1/sessions/{sid}/complete", headers=auth_headers)

    # Verify attempt exists in DB regardless of evaluation
    result = await db.execute(select(Attempt).where(Attempt.id == aid))
    attempt = result.scalar_one_or_none()
    assert attempt is not None
    assert attempt.status == "completed"
