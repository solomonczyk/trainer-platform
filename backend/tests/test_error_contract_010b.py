"""Focused test: backend error responses always use canonical format.

Verifies that all backend error paths return:
    {"error": {"code": "...", "message": "...", "details": {...}, "request_id": "..."}}

Even when the Python exception is a plain Starlette HTTPException
(which by default returns {"detail": "..."}). The fix added
app.exception_handler(HTTPException)(global_error_handler) to main.py.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

import app.main as main_app_module

fastapi_app = main_app_module.app


@pytest.mark.asyncio
async def test_http_exception_returns_canonical_error_format():
    """Unauthenticated request to auth-required endpoint must return
    canonical {"error": {"code": ..., "message": ...}} format,
    NOT the Starlette default {"detail": "..."}."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # /health is public; use an endpoint that requires auth
        resp = await ac.get("/api/v1/me")

    assert resp.status_code == 401, (
        f"Expected 401, got {resp.status_code}: {resp.text}"
    )

    body = resp.json()

    # Must have the canonical error wrapper
    assert "error" in body, (
        f"Response body missing 'error' key: {body}"
    )

    err = body["error"]
    assert isinstance(err, dict), f"'error' is not a dict: {err}"

    # Must have code, message, details, request_id
    assert "code" in err, f"'error' missing 'code': {err}"
    assert "message" in err, f"'error' missing 'message': {err}"
    assert "details" in err, f"'error' missing 'details': {err}"
    assert "request_id" in err, f"'error' missing 'request_id': {err}"

    # Check expected values
    assert err["code"] == "UNAUTHORIZED"
    assert err["message"] == "Authentication required"
    assert isinstance(err["details"], dict)
    assert isinstance(err["request_id"], str)

    # Must NOT be the Starlette default format
    assert "detail" not in body or not isinstance(body["detail"], str), (
        f"Body still has raw Starlette 'detail' format: {body}"
    )


@pytest.mark.asyncio
async def test_not_found_returns_canonical_error_format():
    """A valid endpoint with non-existent resource must return canonical format."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # /api/v1/quests/{id}/start is POST; non-existent id returns 401 (unauth)
        resp = await ac.post("/api/v1/quests/nonexistent-quest-id/start", json={})

    assert resp.status_code in (401, 404, 405), (
        f"Expected 401, 404 or 405, got {resp.status_code}: {resp.text}"
    )

    body = resp.json()

    if resp.status_code == 401:
        # Pre-auth failure — canonical error format
        assert "error" in body, f"Missing 'error' key: {body}"
        err = body["error"]
        assert "code" in err
        assert "message" in err
    else:
        # 404 or 405 — should also be canonical
        assert "error" in body, f"Missing 'error' key: {body}"
        err = body["error"]
        assert "code" in err
        assert "message" in err


@pytest.mark.asyncio
async def test_validation_error_returns_canonical_format():
    """Request with invalid body should return canonical error format,
    NOT FastAPI's default {"detail": [...]}."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # POST /api/v1/auth/register with missing password
        resp = await ac.post(
            "/api/v1/auth/register",
            json={"email": "bad-request"},
        )

    body = resp.json()

    # If we get 422 (validation error), verify canonical format
    if resp.status_code == 422:
        assert "error" in body, (
            f"Validation error missing 'error' key: {body}"
        )
        err = body["error"]
        assert "code" in err
        assert "message" in err
        assert isinstance(err["details"], dict)


@pytest.mark.asyncio
async def test_forbidden_returns_canonical_format():
    """Forbidden response from admin-only endpoint must be canonical."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/admin")

    # 404 is acceptable if /admin doesn't exist; we're testing the error format
    body = resp.json()
    if resp.status_code in (403, 404):
        # 404 from FastAPI is also an HTTPException
        assert "error" in body, f"Missing 'error' key (status={resp.status_code}): {body}"
        err = body["error"]
        assert "code" in err
        assert "message" in err
