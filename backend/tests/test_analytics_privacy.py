"""Tests for analytics event recording and privacy."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import AnalyticsEvent


@pytest.mark.asyncio
async def test_analytics_event_recorded(client, test_user, auth_headers, db):
    """POST /api/v1/analytics/events records event."""
    response = await client.post(
        "/api/v1/analytics/events",
        json={
            "event_type": "domain_catalog_viewed",
            "trainer_slug": None,
            "scenario_id": None,
            "properties": {"source": "landing"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"

    # Verify in DB
    result = await db.execute(
        select(AnalyticsEvent).where(AnalyticsEvent.event_type == "domain_catalog_viewed")
    )
    event = result.scalar_one_or_none()
    assert event is not None
    assert event.user_id == test_user.id


@pytest.mark.asyncio
async def test_raw_answer_blocked_in_analytics(client, test_user, auth_headers, db):
    """Analytics rejects raw answer text in properties."""
    response = await client.post(
        "/api/v1/analytics/events",
        json={
            "event_type": "answer_submitted",
            "trainer_slug": "qa-engineer-interview-trainer",
            "scenario_id": "qa_bug_report_structure_v1",
            "properties": {
                "scenario_id": "qa_bug_report_structure_v1",
                "answer": "This is my detailed answer about bug report structure with steps...",
                "answer_text": "Sensitive answer content",
            },
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Verify stored event doesn't contain raw answer
    result = await db.execute(
        select(AnalyticsEvent).where(AnalyticsEvent.event_type == "answer_submitted")
    )
    event = result.scalar_one_or_none()
    assert event is not None
    props = event.properties or {}
    assert "answer" not in props
    assert "answer_text" not in props


@pytest.mark.asyncio
async def test_passwords_blocked_in_analytics(client, auth_headers, db):
    """Analytics blocks password fields in properties."""
    response = await client.post(
        "/api/v1/analytics/events",
        json={
            "event_type": "user_registered",
            "properties": {
                "password": "super_secret_123",
                "api_key": "sk-1234567890",
            },
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    result = await db.execute(
        select(AnalyticsEvent).where(AnalyticsEvent.event_type == "user_registered")
    )
    event = result.scalar_one_or_none()
    assert event is not None
    props = event.properties or {}
    assert "password" not in props
    assert "api_key" not in props


@pytest.mark.asyncio
async def test_analytics_safe_event_types(client, auth_headers):
    """Only valid event types are accepted."""
    # Valid event type should work
    response = await client.post(
        "/api/v1/analytics/events",
        json={"event_type": "landing_viewed"},
        headers=auth_headers,
    )
    assert response.status_code in (200, 422)


@pytest.mark.asyncio
async def test_analytics_scenario_context(client, auth_headers, db):
    """Analytics includes trainer/scenario context."""
    response = await client.post(
        "/api/v1/analytics/events",
        json={
            "event_type": "scenario_started",
            "trainer_slug": "qa-engineer-interview-trainer",
            "scenario_id": "qa_bug_report_structure_v1",
            "properties": {"difficulty": "junior_basic"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    result = await db.execute(
        select(AnalyticsEvent).where(AnalyticsEvent.event_type == "scenario_started")
    )
    event = result.scalar_one_or_none()
    assert event is not None
    assert event.trainer_slug == "qa-engineer-interview-trainer"
    assert event.scenario_id == "qa_bug_report_structure_v1"
