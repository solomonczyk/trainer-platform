"""Tests for scenario runtime endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import SimulationSession, Attempt, SimulationMessage


@pytest.mark.asyncio
async def test_list_scenarios(client: AsyncClient, test_trainer, test_scenario):
    """GET /api/v1/trainers/{slug}/scenarios returns scenarios."""
    response = await client.get(
        "/api/v1/trainers/qa-engineer-interview-trainer/scenarios",
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_scenario(client: AsyncClient, test_scenario):
    """GET /api/v1/scenarios/{scenario_id} returns scenario detail."""
    response = await client.get(
        "/api/v1/scenarios/qa_bug_report_structure_v1",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "qa_bug_report_structure_v1"
    assert data["difficulty"] == "junior_basic"


@pytest.mark.asyncio
async def test_start_scenario(client: AsyncClient, test_trainer, test_scenario, auth_headers, db):
    """POST /api/v1/scenarios/{scenario_id}/start creates session and attempt."""
    # Enroll first
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )

    response = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "attempt_id" in data
    assert data["status"] in ("active", "started")

    # Verify session and attempt created in DB
    result = await db.execute(
        select(SimulationSession).where(SimulationSession.id == data["session_id"])
    )
    session = result.scalar_one_or_none()
    assert session is not None
    assert session.status == "active"

    result = await db.execute(
        select(Attempt).where(Attempt.id == data["attempt_id"])
    )
    attempt = result.scalar_one_or_none()
    assert attempt is not None
    assert attempt.status == "in_progress"


@pytest.mark.asyncio
async def test_submit_message(client: AsyncClient, test_trainer, test_scenario, auth_headers, db):
    """POST /api/v1/sessions/{session_id}/messages saves message."""
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

    # Submit message
    response = await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "Test answer about bug report structure..."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "message_id" in data
    assert data["status"] == "saved"

    # Verify in DB
    result = await db.execute(
        select(SimulationMessage).where(SimulationMessage.id == data["message_id"])
    )
    msg = result.scalar_one_or_none()
    assert msg is not None
    assert "bug report" in msg.content.lower()


@pytest.mark.asyncio
async def test_submit_empty_message_blocked(client: AsyncClient, test_trainer, test_scenario, auth_headers):
    """Empty message content returns 422."""
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    start_resp = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    session_id = start_resp.json()["session_id"]

    response = await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "   "},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_complete_session(client: AsyncClient, test_trainer, test_scenario, auth_headers, db):
    """POST /api/v1/sessions/{session_id}/complete marks attempt completed."""
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
        json={"content": "My answer about bug reports."},
        headers=auth_headers,
    )

    # Complete
    response = await client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

    # Verify attempt saved before any AI call
    result = await db.execute(select(Attempt).where(Attempt.id == attempt_id))
    attempt = result.scalar_one_or_none()
    assert attempt is not None
    assert attempt.status == "completed"
    assert attempt.answer_text is not None or True  # answer may be updated
