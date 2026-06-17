"""Tests for email verification flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.email import InMemoryEmailSender
from app.db.models import User
from app.modules.auth.repository import set_verification_token, get_user_by_email
from app.core.config import settings


def _auth(token: str) -> dict:
    """Build an Authorization header dict from a bearer token."""
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_registration_creates_unverified_user(
    client: AsyncClient,
    fake_email_sender: InMemoryEmailSender,
):
    """On registration, user is created with email_verified=False and a token is set.
    Exactly one verification email is sent.
    """
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

    # Exactly one verification email sent
    assert fake_email_sender.sent_count == 1


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
async def test_unauthenticated_verify_blocked(client: AsyncClient):
    """Verify-email requires authentication; unauthenticated requests get 401."""
    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "some-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_verifies_user(
    client: AsyncClient,
    db: AsyncSession,
):
    """A valid verification token marks the user's email as verified.
    Requires authenticated request from the token owner."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "verify_me@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201
    auth = _auth(reg_resp.json()["access_token"])

    # Fetch the user's token from DB
    user = await get_user_by_email(db, "verify_me@test.com")
    assert user is not None
    assert user.email_verification_token is not None
    assert user.email_verified is False

    # Verify the email via the API (authenticated as the token owner)
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": user.email_verification_token},
        headers=auth,
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
    """An expired verification token is rejected (authenticated)."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "expired_token@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201
    auth = _auth(reg_resp.json()["access_token"])

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
        headers=auth,
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
    auth = _auth(reg_resp.json()["access_token"])

    user = await get_user_by_email(db, "reuse_token@test.com")
    assert user is not None
    assert user.email_verification_token is not None

    token = user.email_verification_token

    # First verification — should succeed
    verify1 = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
        headers=auth,
    )
    assert verify1.status_code == 200

    # Second verification with same token — should fail (token consumed/cleared)
    verify2 = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
        headers=auth,
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
    fake_email_sender: InMemoryEmailSender,
):
    """Resend verification generates a new token and sends one email."""
    # Register a new user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "resend_test@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201

    # Wait for cooldown to expire (the resend service checks _recently_sent)
    user = await get_user_by_email(db, "resend_test@test.com")
    assert user is not None
    old_token = user.email_verification_token
    assert old_token is not None

    # Manually set token expiry to long ago so resend is allowed
    far_past = datetime.now(timezone.utc) - timedelta(hours=48)
    await set_verification_token(
        db,
        user,
        old_token,
        far_past + timedelta(hours=settings.email_verification_token_expire_hours),
    )
    await db.commit()

    fake_email_sender.reset()

    # Resend verification
    resend_resp = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_test@test.com"},
    )
    assert resend_resp.status_code in (200,)
    data = resend_resp.json()
    assert data["sent"] is True

    # Verify token has changed
    await db.refresh(user)
    assert user.email_verification_token is not None
    assert user.email_verification_token != old_token

    # Exactly one email sent for the resend
    assert fake_email_sender.sent_count == 1


@pytest.mark.asyncio
async def test_verify_email_unknown_token(
    client: AsyncClient,
    auth_headers: dict,
):
    """A non-existent token returns 404 (auth required but token not in DB)."""
    response = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "this-token-does-not-exist"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_wrong_user_verify_blocked(
    client: AsyncClient,
    db: AsyncSession,
):
    """A user cannot verify another user's token."""
    # Register user A
    reg_a = await client.post(
        "/api/v1/auth/register",
        json={"email": "user_a@test.com", "password": "password123"},
    )
    assert reg_a.status_code == 201
    user_a = await get_user_by_email(db, "user_a@test.com")
    assert user_a is not None
    assert user_a.email_verification_token is not None
    token_a = user_a.email_verification_token

    # Register user B and use B's auth to verify A's token
    reg_b = await client.post(
        "/api/v1/auth/register",
        json={"email": "user_b@test.com", "password": "password123"},
    )
    assert reg_b.status_code == 201
    auth_b = _auth(reg_b.json()["access_token"])

    # User B tries to verify user A's token — should be blocked
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": token_a},
        headers=auth_b,
    )
    assert verify_resp.status_code == 403
    data = verify_resp.json()
    assert "FORBIDDEN" in str(data)


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
    auth = _auth(reg_resp.json()["access_token"])

    user = await get_user_by_email(db, "token_consumed@test.com")
    assert user is not None
    assert user.email_verification_token is not None
    original_token = user.email_verification_token

    # Verify
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": original_token},
        headers=auth,
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
    fake_email_sender: InMemoryEmailSender,
):
    """A verified user cannot resend verification (returns sent=False)."""
    # Register and verify
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "resend_blocked@test.com", "password": "password123"},
    )
    assert reg_resp.status_code == 201
    auth = _auth(reg_resp.json()["access_token"])

    user = await get_user_by_email(db, "resend_blocked@test.com")
    token = user.email_verification_token

    await client.post("/api/v1/auth/verify-email", json={"token": token}, headers=auth)

    fake_email_sender.reset()

    # Try resend
    resend_resp = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_blocked@test.com"},
    )
    assert resend_resp.status_code == 200  # Safe response
    data = resend_resp.json()
    assert data["sent"] is False
    assert data["message_code"] == "already_verified"
    # No email sent
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_login_verified_user_does_not_send_verification_email(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Login with a verified user does not reset email_verified or send email."""
    # Register and verify a user
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "login_verified@test.com", "password": "password123"},
    )
    assert reg.status_code == 201

    # Manually verify in DB
    user = await get_user_by_email(db, "login_verified@test.com")
    assert user is not None
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None
    await db.commit()

    fake_email_sender.reset()

    # Login — response must show email_verified=true
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_verified@test.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["user"]["email_verified"] is True

    # /me must also return email_verified=true
    token = data["access_token"]
    me_resp = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email_verified"] is True

    # No email sent during login
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_duplicate_registration_no_verification_email(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Registering with an already verified email does NOT create a new user or send email."""
    root = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup_no_email@test.com", "password": "password123"},
    )
    assert root.status_code == 201

    # Verify in DB
    user = await get_user_by_email(db, "dup_no_email@test.com")
    assert user is not None
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None
    await db.commit()

    fake_email_sender.reset()

    # Try registering again — should be rejected
    dup = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup_no_email@test.com", "password": "password123"},
    )
    assert dup.status_code == 409

    # Verify only ONE user exists for this email
    result = await db.execute(
        select(User).where(User.email == "dup_no_email@test.com")
    )
    users = result.scalars().all()
    assert len(users) == 1

    # Original user still verified
    assert users[0].email_verified is True

    # No email sent for duplicate registration
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_me_returns_db_email_verified_true(
    client: AsyncClient,
    db: AsyncSession,
):
    """/me returns email_verified=true for a verified user (reads from DB)."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "me_verified@test.com", "password": "password123"},
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
    user = await get_user_by_email(db, "me_verified@test.com")
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


# ============================================================================
# New tests for resend throttling and behavior
# ============================================================================

@pytest.mark.asyncio
async def test_resend_verification_explicit_and_throttled(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Explicit resend sends one email and subsequent attempts are throttled."""
    # Create an unverified user
    from app.core.security import hash_password
    user = User(
        email="resend_throttle@example.com",
        password_hash=hash_password("testpass123"),
        email_verified=False,
    )
    db.add(user)
    await db.commit()

    fake_email_sender.reset()

    # First resend should work (need to also set a token that's old enough)
    user = await get_user_by_email(db, "resend_throttle@example.com")
    assert user is not None

    # Set a very old token to bypass cooldown check
    far_past = datetime.now(timezone.utc) - timedelta(hours=48)
    await set_verification_token(
        db,
        user,
        "old-test-token",
        far_past + timedelta(hours=settings.email_verification_token_expire_hours),
    )
    await db.commit()

    # First resend — should succeed
    r1 = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_throttle@example.com"},
    )
    assert r1.status_code == 200
    assert r1.json()["sent"] is True
    assert fake_email_sender.sent_count == 1

    # Second resend immediately — should be rate-limited
    r2 = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "resend_throttle@example.com"},
    )
    assert r2.status_code == 200  # Safe response
    assert r2.json()["sent"] is False
    assert r2.json()["message_code"] == "rate_limited_or_recently_sent"
    # No additional email
    assert fake_email_sender.sent_count == 1


@pytest.mark.asyncio
async def test_resend_unknown_email(
    client: AsyncClient,
    fake_email_sender: InMemoryEmailSender,
):
    """Resend for unknown email returns safe response (no enumeration)."""
    response = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sent"] is False
    assert data["message_code"] == "if_account_exists_email_sent"
    assert fake_email_sender.sent_count == 0


@pytest.mark.asyncio
async def test_resend_already_verified(
    client: AsyncClient,
    db: AsyncSession,
    fake_email_sender: InMemoryEmailSender,
):
    """Resend for an already verified account returns sent=False."""
    from app.core.security import hash_password
    user = User(
        email="already_verified_resend@example.com",
        password_hash=hash_password("testpass123"),
        email_verified=True,
    )
    db.add(user)
    await db.commit()

    fake_email_sender.reset()

    response = await client.post(
        "/api/v1/auth/resend-verification",
        json={"email": "already_verified_resend@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sent"] is False
    assert data["message_code"] == "already_verified"
    assert fake_email_sender.sent_count == 0
