"""Tests for domain and trainer catalog endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_domains(client: AsyncClient, test_domain):
    """GET /api/v1/domains returns domains."""
    response = await client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["slug"] == "it"


@pytest.mark.asyncio
async def test_get_domain(client: AsyncClient, test_domain):
    """GET /api/v1/domains/{slug} returns domain detail."""
    response = await client.get("/api/v1/domains/it")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "it"
    assert "trainers" in data


@pytest.mark.asyncio
async def test_get_domain_not_found(client: AsyncClient):
    """GET /api/v1/domains/{slug} with invalid slug returns 404."""
    response = await client.get("/api/v1/domains/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_trainer(client: AsyncClient, test_trainer):
    """GET /api/v1/trainers/{slug} returns trainer detail."""
    response = await client.get("/api/v1/trainers/qa-engineer-interview-trainer")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "qa-engineer-interview-trainer"
    assert data["trainer_product_id"] == "qa_engineer_interview_trainer"


@pytest.mark.asyncio
async def test_get_trainer_not_found(client: AsyncClient):
    """GET /api/v1/trainers/{slug} with invalid slug returns 404."""
    response = await client.get("/api/v1/trainers/nonexistent")
    assert response.status_code == 404
