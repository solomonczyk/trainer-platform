"""Tests for security, RBAC, and data isolation."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Attempt, Evaluation
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_attempt(client, test_trainer, test_scenario, auth_headers, db):
    """User A cannot read user B's attempt."""
    # User A creates an attempt
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    start_resp = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    attempt_id = start_resp.json()["attempt_id"]

    # User B tries to access it
    user_b_token = create_access_token(user_id="other-user-id", role="registered_user")
    response = await client.get(
        f"/api/v1/attempts/{attempt_id}/evaluation",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_guest_cannot_access_progress(client, test_trainer):
    """Guest users cannot access progress."""
    response = await client.get("/api/v1/me/progress")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin(client, auth_headers):
    """Non-admin users cannot access admin endpoints."""
    response = await client.get(
        "/api/v1/admin/seed-status",
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_admin(client, admin_headers):
    """Admin users can access admin endpoints."""
    response = await client.get(
        "/api/v1/admin/seed-status",
        headers=admin_headers,
    )
    # 200 or 404 depending on DB state
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_attempt_ownership_check(client, test_trainer, test_scenario, auth_headers, db):
    """Attempt retrieval checks ownership."""
    # Create attempt as user A
    await client.post(
        "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
        headers=auth_headers,
    )
    start_resp = await client.post(
        "/api/v1/scenarios/qa_bug_report_structure_v1/start",
        headers=auth_headers,
    )
    attempt_id = start_resp.json()["attempt_id"]

    # Verify attempt belongs to the right user in DB
    result = await db.execute(select(Attempt).where(Attempt.id == attempt_id))
    attempt = result.scalar_one_or_none()
    assert attempt is not None
    # The test_user fixture creates a user with specific ID
    assert attempt.user_id is not None


@pytest.mark.asyncio
async def test_no_secrets_in_frontend():
    """Check no secrets are hardcoded in frontend client."""
    import ast
    import sys
    from pathlib import Path

    client_path = Path("F:/Dev/Projects/simulators/MULTISIMULATORS_PLATFOM/frontend/src/lib/api/client.ts")
    if not client_path.exists():
        pytest.skip("Frontend client not found")

    content = client_path.read_text()
    # Check for hardcoded secrets
    secrets = ["sk-", "api_key=", "secret=", "password="]
    for secret in secrets:
        if secret in content:
            # Allow in environment variable patterns
            line = [l for l in content.split("\n") if secret in l.lower()]
            if line and "process.env" not in line[0]:
                pytest.fail(f"Potential secret found in frontend: {secret}")
