# MVP-002 Known Issues

## Layer
TRAINER-PLATFORM-MVP-002-STAGING-DEPLOY-PREPARATION

## Date
2026-06-05

## Critical
None open.

## High
1. **External staging provider not deployed** — No external staging host
   (Render, Railway, Fly.io, etc.) is configured. Local Docker Compose staging
   profile is used instead.
2. **Real OpenAI provider not configured** — AI evaluation uses mock provider;
   real provider needs API key setup in a future layer.
3. **Frontend tests have minimal coverage** — Only 1 test file with 3 tests
   (Button component). Comprehensive frontend testing deferred.

## Medium
4. **Rate limiting uses in-memory store** — Staging rate limiter is in-memory
   (per-worker); for multi-worker deployments, Redis-based rate limiting is
   required.
5. **No monitoring/alerting** — No external monitoring (Sentry, DataDog, etc.)
   configured for staging.
6. **No email infrastructure** — No email verification or password reset flows.
7. **Admin API key not enforced** — Admin API key is defined but admin routes
   rely on JWT role only.

## Low
8. **Mobile responsiveness needs review** — Basic responsive design implemented
   but not fully tested on all devices.
9. **Accessibility audit not performed** — Basic accessibility patterns used
   but no formal audit.
10. **No backup/restore scripts** — Database backup procedures not automated
    for staging.

## Accepted for This Layer
- Local Docker Compose staging instead of external provider
- Mock AI provider instead of real LLM
- No email verification
- No password reset flow
- Minimal admin dashboard
- Basic analytics without visualization
- SQLite for E2E smoke test (tests use isolated in-memory DB)
