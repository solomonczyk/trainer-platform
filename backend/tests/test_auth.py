"""Tests for auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """POST /api/v1/auth/register creates user and returns token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@test.com", "password": "password123", "display_name": "New User"},
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["role"] == "registered_user"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Registering with existing email returns error."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "password123"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """POST /api/v1/auth/login returns token with valid credentials."""
    # First register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Login with wrong password returns error."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_current_user(client: AsyncClient):
    """GET /api/v1/me returns current user info."""
    # Register and login
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@test.com", "password": "password123"},
    )
    token = reg_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["email"] == "me@test.com"
    assert data["role"] == "registered_user"
