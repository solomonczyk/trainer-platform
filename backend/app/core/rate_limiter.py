"""Rate limiter — in-memory sliding window implementation.

Controlled by settings:
  rate_limit_enabled: bool
  rate_limit_requests_per_minute: int

Designed as a simple middleware placeholder.  For production, replace with
Redis-based limiter (or use the API Gateway's built-in rate limiting).
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings
from app.core.errors import AppError


# ---------------------------------------------------------------------------
# In-memory sliding window store
# ---------------------------------------------------------------------------

class _SlidingWindowStore:
    """Per-IP sliding window counter.

    NOT suitable for multi-worker deployments — use Redis in production.
    """

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def _purge(self, key: str, window: float) -> None:
        now = time.monotonic()
        cutoff = now - window
        self._buckets[key] = [t for t in self._buckets[key] if t > cutoff]
        if not self._buckets[key]:
            del self._buckets[key]

    def allow(self, key: str, max_requests: int, window: float = 60.0) -> bool:
        self._purge(key, window)
        current = len(self._buckets[key])
        if current >= max_requests:
            return False
        self._buckets[key].append(time.monotonic())
        return True

    def remaining(self, key: str, max_requests: int, window: float = 60.0) -> int:
        self._purge(key, window)
        return max(0, max_requests - len(self._buckets[key]))


_store = _SlidingWindowStore()


def reset_store() -> None:
    """Clear all rate-limit buckets.  Used between tests."""
    _store._buckets.clear()


# ---------------------------------------------------------------------------
# ASGI middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate-limiting HTTP middleware.

    Adds X-RateLimit headers to every response.  Returns 429 when the limit
    is exceeded and rate limiting is enabled.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Use client IP or X-Forwarded-For as the key
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        key = forwarded.split(",")[0].strip() if forwarded else client_ip

        max_r = settings.rate_limit_requests_per_minute

        if not _store.allow(key, max_r, window=60.0):
            retry_after = 60  # seconds
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests — please slow down.",
                        "details": {"retry_after_seconds": retry_after},
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_r),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        remaining = _store.remaining(key, max_r, window=60.0)
        response.headers["X-RateLimit-Limit"] = str(max_r)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
