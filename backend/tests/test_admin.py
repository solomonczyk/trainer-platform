"""Tests for admin endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_seed_status(client, admin_headers):
    """GET /api/v1/admin/seed-status returns seed info."""
    response = await client.get(
        "/api/v1/admin/seed-status",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert "trainers" in data
    assert "scenarios" in data


@pytest.mark.asyncio
async def test_admin_system_health(client, admin_headers):
    """GET /api/v1/admin/system-health returns health info."""
    response = await client.get(
        "/api/v1/admin/system-health",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_admin_analytics_sanity(client, admin_headers):
    """GET /api/v1/admin/analytics/sanity returns analytics info."""
    response = await client.get(
        "/api/v1/admin/analytics/sanity",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data


@pytest.mark.asyncio
async def test_admin_evaluation_failures(client, admin_headers):
    """GET /api/v1/admin/evaluations/failures returns failures list."""
    response = await client.get(
        "/api/v1/admin/evaluations/failures",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
