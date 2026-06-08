# 004C Root Cause Report — E2E Stabilization

## Migration Test Infrastructure

- **Root cause**: Migration tests 005/006 depended on a locally named Docker container `trainer-migration-pg` that does not exist on GitHub Actions runners.
- **Fix**: Added PostgreSQL 16 service to the `backend-tests` job with health check, `MIGRATION_DATABASE_URL` env var, Alembic migration setup step, and refactored `_pg()` in both test files to use psycopg2 directly instead of the external `psql` binary.
- **Product regression**: false
- **Test fixture regression**: false  
- **Environment regression**: true (CI infrastructure)

## Cross-Platform SQL Execution

- **Root cause**: `_pg()` function executed `psql` binary when `MIGRATION_DATABASE_URL` was set, but Windows developer environments lack `psql.exe`.
- **Fix**: Replaced `psql` subprocess with `psycopg2.connect()` call — no external binary needed. Added `_to_async_url()` helper to convert sync `postgresql://` URLs to async `postgresql+asyncpg://` for Alembic's `create_async_engine`.
- **Product regression**: false
- **Test fixture regression**: true (test helper)
- **Environment regression**: true

## Backend E2E Smoke

- **Failing test**: `tests/e2e/test_smoke.py::test_full_user_journey`
- **Stage**: N/A — test passed locally and in CI after infrastructure fixes.
- **Root cause**: The test was never reached in previous CI runs because `-x` (exit on first failure) stopped at the migration test failure. After migration fix, the E2E test passes.
- **Product regression**: false
- **Test fixture regression**: false
- **Environment regression**: false

## QA Engineer Interview Trainer React Error #31

- **Root cause**: QA Engineer Interview Trainer scenarios define `target_skills` as an array of objects (`{skill_id, weight}`) instead of strings. The frontend rendered `{skill}` directly, causing React error #31 ("Objects are not valid as a React child").
- **Fix**: Updated three JSX locations to check `typeof skill === "string"` before rendering. For object skills, render `skill.skill_id`. Updated `ScenarioDetail` type to accept both `string` and `{skill_id, weight}` variants.
- **Product regression**: true (rendering defect)
- **Test fixture regression**: false

## Authentication /api/v1/me

- **Root cause**: The auth flow already handles unauthenticated `/me` requests gracefully — `getCurrentUser()` catches errors and sets `user = null`. No infinite retry loop. No console error storm.
- **Fix**: None required — existing behavior is correct.
- **Product regression**: false

## Favicon 404

- **Root cause**: No favicon file existed in `frontend/public/` and no `<link>` tag was configured.
- **Fix**: Added SVG favicon to `frontend/public/favicon.svg` and `Favicon` component in layout that injects the link tag.
- **Product regression**: false
