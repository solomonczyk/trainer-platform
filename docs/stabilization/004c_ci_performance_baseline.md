# 004C CI Performance Baseline

## Measurement Method

All durations measured from GitHub Actions workflow run #109 (commit d75d80f).

## Job Durations

| Step | Duration (approx) |
|------|------------------|
| Dependency installation (pip) | ~45s |
| PostgreSQL readiness check | ~5s |
| Alembic migration setup | ~25s |
| Migration tests (005 + 006, 10 tests) | ~14s |
| Certification core (SQLite, excl. migration) | ~420s |
| General tests (SQLite) | ~120s |
| E2E smoke test | ~5s |
| Frontend tests (Vitest) | ~3s |
| Frontend TypeScript check | ~15s |
| Frontend build (Next.js) | ~60s |
| OpenAPI export | ~20s |
| **Total workflow duration** | **~12-15 min** |

## Slowest Test Groups

1. **Certification core (SQLite)** — ~420s (largest test file count)
2. **General tests (SQLite)** — ~120s
3. **Frontend build** — ~60s

## Observations

- The certification core SQLite tests dominate the backend runtime (~7 min).
- Migration tests complete quickly (~14s) thanks to isolated PostgreSQL service.
- Frontend build and tests are fast (~3 min combined).
- Cached pip/npm dependencies significantly reduce install time.

## Future Optimization Targets

1. Split certification core into smaller parallel groups
2. Use `pytest-xdist` for parallel test execution (after isolation verification)
3. Cache more aggressively for pip

## Baseline Recorded

- Date: 2026-06-08
- CI run: #109
- Workflow file: `.github/workflows/ci.yml`
- Status: success
