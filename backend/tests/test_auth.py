"""Tests for auth endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.core.email import InMemoryEmailSender


@pytest.mark.asyncio
async def test_register(client: AsyncClient, fake_email_sender: InMemoryEmailSender):
    """POST /api/v1/auth/register creates user and returns token.
    A verification email is sent for truly new accounts.
    """
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
    # Verification email sent
    assert fake_email_sender.sent_count == 1


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, fake_email_sender: InMemoryEmailSender):
    """Registering with existing email returns error and does NOT send email."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "password123"},
    )
    # Reset sent count from first registration
    fake_email_sender.reset()
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "password123"},
    )
    assert response.status_code == 409
    # No additional email sent for duplicate registration
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_login(client: AsyncClient, fake_email_sender: InMemoryEmailSender):
    """POST /api/v1/auth/login returns token with valid credentials.
    Login never sends a verification email.
    """
    # First register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    fake_email_sender.reset()
    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"
    # Login does not send verification email
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, fake_email_sender: InMemoryEmailSender):
    """Login with wrong password returns error and does not send email."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert fake_email_sender.sent_count == 0


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


@pytest.mark.asyncio
async def test_register_case_insensitive_email(client: AsyncClient):
    """Register with mixed case, then login with lowercase succeeds."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "MixedCase@Test.com", "password": "password123"},
    )
    # Login with lowercase should succeed
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "mixedcase@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_verified_email_rejected(
    client: AsyncClient,
    fake_email_sender: InMemoryEmailSender,
):
    """Registering again when the email exists (verified) returns 409 CONFLICT.
    No email is sent for the duplicate attempt.
    """
    # Register and verify email
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "existing_verified@test.com", "password": "password123"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    user_resp = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert user_resp.status_code == 200

    fake_email_sender.reset()

    # Register again with the same email — should be rejected
    resp2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "existing_verified@test.com", "password": "password123"},
    )
    assert resp2.status_code == 409
    data = resp2.json()
    assert "already exists" in data["error"]["message"].lower()
    # No email sent for duplicate registration
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_register_case_insensitive_duplicate_rejected(
    client: AsyncClient,
    fake_email_sender: InMemoryEmailSender,
):
    """Register with one casing, then register with different casing — rejected.
    No email is sent for the duplicate attempt.
    """
    await client.post(
        "/api/v1/auth/register",
        json={"email": "Original@Test.com", "password": "password123"},
    )
    fake_email_sender.reset()
    # Different casing — now caught by case-insensitive lookup
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "original@test.com", "password": "password123"},
    )
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["error"]["message"].lower()
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_login_verified_user_returns_email_verified_true(
    client: AsyncClient, db: AsyncSession, fake_email_sender: InMemoryEmailSender
):
    """Login response includes email_verified=true for a verified user.
    Login does not send a verification email.
    """
    # Register — user starts unverified
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "verify_login@test.com", "password": "password123"},
    )
    assert reg.status_code == 201

    # Manually verify the user in DB (simulating email verification)
    user = (await db.execute(
        select(User).where(User.email == "verify_login@test.com")
    )).scalar_one()
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None
    # Commit so the API session sees the change and doesn't conflict on SQLite
    await db.commit()

    fake_email_sender.reset()

    # Login — response must show email_verified=true
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "verify_login@test.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["user"]["email_verified"] is True
    # Login does not send verification email
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_login_updates_last_login(client: AsyncClient, db: AsyncSession):
    """Login updates the user's last_login_at timestamp."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logintime@test.com", "password": "password123"},
    )
    # Before login, last_login_at should be None
    user = (await db.execute(
        select(User).where(User.email == "logintime@test.com")
    )).scalar_one()
    original = user.last_login_at
    # Commit so the test session doesn't hold a lock conflicting with the API
    await db.commit()

    await client.post(
        "/api/v1/auth/login",
        json={"email": "logintime@test.com", "password": "password123"},
    )
    await db.refresh(user)
    assert user.last_login_at is not None
    assert user.last_login_at != original


# ============================================================================
# New tests for LAYER-011-AUTH-IDENTITY-EMAIL-SPAM-AND-VERIFICATION-STATE-FIX
# ============================================================================

@pytest.mark.asyncio
async def test_verified_user_login_does_not_send_verification_email(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """A verified user logging in must NOT send any verification email."""
    # Create verified user directly in DB
    from app.core.security import hash_password
    user = User(
        email="verified_login@example.com",
        password_hash=hash_password("testpass123"),
        email_verified=True,
    )
    db.add(user)
    await db.commit()

    fake_email_sender.reset()

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "verified_login@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["email_verified"] is True
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_register_existing_verified_email_no_duplicate_no_email(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Registering with an already verified email must:
    - Not create a duplicate user
    - Not send any verification email
    - Return 409 Conflict
    """
    from app.core.security import hash_password
    user = User(
        email="dup_verified@example.com",
        password_hash=hash_password("testpass123"),
        email_verified=True,
    )
    db.add(user)
    await db.commit()

    fake_email_sender.reset()

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup_verified@example.com", "password": "newpass123"},
    )
    assert response.status_code == 409

    # Verify only one user exists
    result = await db.execute(
        select(User).where(User.email == "dup_verified@example.com")
    )
    users = result.scalars().all()
    assert len(users) == 1
    assert users[0].email_verified is True

    # No email sent
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_register_existing_unverified_email_does_not_auto_resend(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Registering with an existing unverified email must:
    - Not auto-resend a verification email
    - Return 409 Conflict
    - Not create a duplicate user
    """
    from app.core.security import hash_password
    user = User(
        email="pending_dup@example.com",
        password_hash=hash_password("testpass123"),
        email_verified=False,
    )
    db.add(user)
    await db.commit()

    fake_email_sender.reset()

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "pending_dup@example.com", "password": "newpass123"},
    )
    assert response.status_code == 409

    # Verify no duplicate created
    result = await db.execute(
        select(User).where(User.email == "pending_dup@example.com")
    )
    users = result.scalars().all()
    assert len(users) == 1

    # No auto-resend
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_me_returns_db_email_verified_true(
    client: AsyncClient,
    db: AsyncSession,
):
    """/me returns email_verified=true for a verified user (reads from DB)."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "me_verify_db@test.com", "password": "password123"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]

    # /me should reflect DB state (unverified initially)
    me1 = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me1.status_code == 200
    assert me1.json()["email_verified"] is False

    # Verify in DB
    user = await db.execute(
        select(User).where(User.email == "me_verify_db@test.com")
    )
    user = user.scalar_one()
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None
    await db.commit()

    # /me must now return email_verified=true — reading fresh DB state
    me2 = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me2.status_code == 200
    assert me2.json()["email_verified"] is True
