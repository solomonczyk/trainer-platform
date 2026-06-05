# Trainer Platform — Staging Smoke Test Report

## Layer
TRAINER-PLATFORM-MVP-002-STAGING-DEPLOY-PREPARATION

## Date
2026-06-05

## Status
PASSED

## Test Method

Smoke tests were executed against the local Docker Compose staging environment:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: PostgreSQL (containerized)

## Results

### Health / Ready

| Endpoint | Status | Response |
|----------|--------|----------|
| `/health` | ✅ PASS | `{"status": "ok", "app": "TrainerPlatform", "version": "0.1.0"}` |
| `/ready` | ✅ PASS | `{"status": "ok", "database": "ok"}` |

### OpenAPI

| Endpoint | Status | Details |
|----------|--------|---------|
| `/openapi.json` | ✅ PASS | HTTP 200, 24 paths exported |

### Frontend

| Page | Status | HTTP Status |
|------|--------|-------------|
| Landing | ✅ PASS | 200 |

### E2E Smoke Test (Full User Journey)

The Python E2E smoke test (`tests/e2e/test_smoke.py`) was executed:

| Step | Status |
|------|--------|
| 1. Health check | ✅ PASS |
| 2. Register | ✅ PASS |
| 3. Login | ✅ PASS |
| 4. Current user | ✅ PASS |
| 5. List domains | ✅ PASS |
| 6. Get domain | ✅ PASS |
| 7. Get trainer | ✅ PASS |
| 8. Enroll | ✅ PASS |
| 9. List scenarios | ✅ PASS |
| 10. Start scenario | ✅ PASS |
| 11. Submit answer | ✅ PASS |
| 12. Complete session | ✅ PASS |
| 13. Evaluate attempt | ✅ PASS (score in range 0-100) |
| 14. Get evaluation | ✅ PASS |
| 15. Check progress | ✅ PASS |
| 16. Trainer-specific progress | ✅ PASS |
| 17. Analytics event | ✅ PASS |
| 18. Profile update | ✅ PASS |

**Overall: ✅ PASSED**

### Analytics Privacy

| Test | Status |
|------|--------|
| Analytics event recorded | ✅ PASS |
| Raw answer blocked in analytics | ✅ PASS |
| Passwords blocked in analytics | ✅ PASS |
| Safe event types | ✅ PASS |
| Scenario context present | ✅ PASS |

### Database / Seed Verification

| Item | Status |
|------|--------|
| Migration applied (001) | ✅ PASS |
| Domain "it" created | ✅ PASS |
| QA Engineer Interview Trainer created | ✅ PASS |
| Trainer version 1.0.0 | ✅ PASS |
| 5 scenarios created | ✅ PASS |
| Rubrics created (5) | ✅ PASS |
| Locales (ru-RU, en-US) created | ✅ PASS |
| Feature flags seeded | ✅ PASS |
| Admin user created | ✅ PASS |

## Test User

All smoke tests used synthetic test data:
- Email: `e2e@test.com`
- Password: `e2etest123`
- Display name: `E2E User`

No real user data was used.

## Raw Answers in Analytics

Confirmed: Raw answers are NOT present in analytics event payloads.
Verified by `test_raw_answer_blocked_in_analytics` test.
