"""Tests for enrollment endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import UserTrainerEnrollment, TrainerProgress


@pytest.mark.asyncio
async def test_enroll_user(client: AsyncClient, test_trainer, auth_headers):
    """POST /api/v1/trainers/{slug}/enroll creates enrollment."""
    response = await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["status"] in ("enrolled", "already_enrolled")


@pytest.mark.asyncio
async def test_enroll_idempotent(client: AsyncClient, test_trainer, auth_headers):
    """Enrolling twice returns already_enrolled status."""
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    response = await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    assert response.status_code in (200, 201)
    assert response.json()["status"] == "already_enrolled"


@pytest.mark.asyncio
async def test_enroll_requires_auth(client: AsyncClient, test_trainer):
    """Enrolling without auth returns error."""
    response = await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_enroll_nonexistent_trainer(client: AsyncClient, auth_headers):
    """Enrolling in non-existent trainer returns 404."""
    response = await client.post(
        "/api/v1/trainers/nonexistent-trainer/enroll",
        headers=auth_headers,
    )
    assert response.status_code == 404
