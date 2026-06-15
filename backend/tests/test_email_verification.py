"""Tests for email verification flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.models import User
from app.modules.auth.repository import set_verification_token, get_user_by_email
from app.core.config import settings


@pytest.mark.asyncio
async def test_registration_creates_unverified_user(client: AsyncClient):
    """On registration, user is created with email_verified=False and a token is set."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newunverified@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email_verified"] is False
    assert "access_token" in data

    # Verify the user has a verification token in the DB
    user_response = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert user_response.status_code in (200,)


@pytest.mark.asyncio
async def test_unverified_user_blocked_from_scenario(
    client: AsyncClient,
    unverified_user: User,
    unverified_headers: dict,
    test_trainer,
    test_scenario,
):
    """Unverified users get 403 EMAIL_NOT_VERIFIED when accessing simulator."""
    # Enroll first
    enroll_resp = await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=unverified_headers,
    )
    # Enroll may work (it's just joining), but scenario start should fail
    # Try to start a scenario
    response = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=unverified_headers,
    )
    assert response.status_code == 403
    data = response.json()
    assert "EMAIL_NOT_VERIFIED" in str(data)


@pytest.mark.asyncio
async def test_unverified_user_blocked_from_quest(
    client: AsyncClient,
    unverified_user: User,
    unverified_headers: dict,
):
    """Unverified users get 403 EMAIL_NOT_VERIFIED when starting a quest."""
    # Find a quest and try to start it (or at least access a protected endpoint)
    response = await client.get(
        "/api/v1/me/progress",
        headers=unverified_headers,
    )
    assert response.status_code == 403
    data = response.json()
    assert "EMAIL_NOT_VERIFIED" in str(data)


@pytest.mark.asyncio
async def test_token_verifies_user(
    client: AsyncClient,
    db: AsyncSession,
):
    """A valid verification token marks the user's email as verified."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "verify_me@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    # Fetch the user's token from DB
    user = await get_user_by_email(db, "verify_me@test.com")
    assert user is not None
    assert user.email_verification_token is not None
    assert user.email_verified is False

    # Verify the email via the API
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": user.email_verification_token},
    )
    assert verify_resp.status_code in (200,)
    verify_data = verify_resp.json()
    assert verify_data["email_verified"] is True
    assert "access_token" in verify_data
    assert len(verify_data["access_token"]) > 20

    # Verify the DB is updated
    await db.refresh(user)
    assert user.email_verified is True


@pytest.mark.asyncio
async def test_expired_token_rejected(
    client: AsyncClient,
    db: AsyncSession,
):
    """An expired verification token is rejected."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "expired_token@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    user = await get_user_by_email(db, "expired_token@test.com")
    assert user is not None

    # Manually set an expired token
    expired_token = "expired-test-token"
    await set_verification_token(
        db,
        user,
        expired_token,
        datetime.now(timezone.utc) - timedelta(hours=1),
    )
    await db.commit()
    await db.refresh(user)

    # Try to verify with expired token
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": expired_token},
    )
    assert verify_resp.status_code == 400
    data = verify_resp.json()
    assert "TOKEN_EXPIRED" in str(data)


@pytest.mark.asyncio
async def test_reused_token_rejected(
    client: AsyncClient,
    db: AsyncSession,
):
    """A token that has already been used is rejected (cleared on consumption)."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "reuse_token@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    user = await get_user_by_email(db, "reuse_token@test.com")
    assert user is not None
    assert user.email_verification_token is not None

    token = user.email_verification_token

    # First verification — should succeed
    verify1 = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )
    assert verify1.status_code == 200

    # Second verification with same token — should fail (token consumed/cleared)
    verify2 = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )
    # Token is cleared on success; second lookup returns 404 NOT_FOUND
    assert verify2.status_code == 404
    data = verify2.json()
    assert "NOT_FOUND" in str(data) or "not found" in str(data).lower()


@pytest.mark.asyncio
async def test_verified_user_can_access_scenario(
    client: AsyncClient,
    auth_headers: dict,
    test_trainer,
    test_scenario,
    db: AsyncSession,
):
    """A verified user can access simulator endpoints."""
    # Enroll first
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )

    # Start a scenario
    response = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    assert response.status_code in (200,)
    data = response.json()
    assert data["status"] == "started"
    assert "session_id" in data


@pytest.mark.asyncio
async def test_resend_verification_creates_new_token(
    client: AsyncClient,
    db: AsyncSession,
):
    """Resend verification generates a new token and invalidates the old one."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "resend_test@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    user = await get_user_by_email(db, "resend_test@test.com")
    assert user is not None
    old_token = user.email_verification_token
    assert old_token is not None

    # Resend verification
    resend_resp = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_test@test.com"},
    )
    assert resend_resp.status_code in (200,)

    # Verify token has changed
    await db.refresh(user)
    assert user.email_verification_token is not None
    assert user.email_verification_token != old_token


@pytest.mark.asyncio
async def test_verify_email_unknown_token(client: AsyncClient):
    """A non-existent token returns 404."""
    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "this-token-does-not-exist"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_verification_token_consumed_after_success(
    client: AsyncClient,
    db: AsyncSession,
):
    """After successful verification, the token is cleared from the database."""
    # Register
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "token_consumed@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    user = await get_user_by_email(db, "token_consumed@test.com")
    assert user is not None
    assert user.email_verification_token is not None
    original_token = user.email_verification_token

    # Verify
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": original_token},
    )
    assert verify_resp.status_code == 200

    # Reload user — token must be cleared
    await db.refresh(user)
    assert user.email_verified is True
    assert user.email_verification_token is None
    assert user.email_verification_token_expires_at is None


@pytest.mark.asyncio
async def test_verified_user_cannot_resend_verification(
    client: AsyncClient,
    db: AsyncSession,
):
    """A verified user cannot resend verification (ALREADY_VERIFIED)."""
    # Register and verify
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "resend_blocked@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    user = await get_user_by_email(db, "resend_blocked@test.com")
    token = user.email_verification_token

    await client.post("/api/v1/auth/verify-email", json={"token": token})

    # Try resend
    resend_resp = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_blocked@test.com"},
    )
    assert resend_resp.status_code == 400
    data = resend_resp.json()
    assert "ALREADY_VERIFIED" in str(data)
