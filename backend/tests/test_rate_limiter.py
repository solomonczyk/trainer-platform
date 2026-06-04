"""Tests for rate limiter middleware."""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_rate_limit_headers_present():
    """Rate limit headers should be present in responses when enabled."""
    from app.core.config import settings
    settings.rate_limit_enabled = True

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert "X-RateLimit-Limit" in r.headers
        assert "X-RateLimit-Remaining" in r.headers

    settings.rate_limit_enabled = False


@pytest.mark.asyncio
async def test_rate_limit_disabled():
    """When disabled, rate limit headers should not be present."""
    from app.core.config import settings
    settings.rate_limit_enabled = False

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert "X-RateLimit-Limit" not in r.headers


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    """Client that exceeds the limit should get 429."""
    from app.core.config import settings

    original = settings.rate_limit_enabled
    settings.rate_limit_enabled = True
    # Set very low limit to trigger 429
    original_limit = settings.rate_limit_requests_per_minute
    settings.rate_limit_requests_per_minute = 3

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First 3 requests should succeed
        for _ in range(3):
            r = await client.get("/health")
            assert r.status_code == 200

        # 4th request should be rejected
        r = await client.get("/health")
        assert r.status_code == 429
        data = r.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    # Reset
    settings.rate_limit_enabled = original
    settings.rate_limit_requests_per_minute = original_limit
