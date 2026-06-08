# CI Feedback Loop Architecture Debt — 004C

## Issue

Full CI pipeline on every commit takes **12–15 minutes** to complete.

## Measured Durations

| Segment | Duration |
|---------|----------|
| Dependency installation (pip + npm) | ~45s |
| PostgreSQL readiness + Alembic migrations | ~30s |
| Migration tests (005 + 006, 10 tests) | ~14s |
| Certification core tests (SQLite) | ~420s |
| General tests (SQLite) | ~120s |
| E2E smoke test | ~5s |
| Frontend tests (Vitest) | ~3s |
| Frontend TypeScript check | ~15s |
| Frontend build (Next.js) | ~60s |
| OpenAPI export | ~20s |
| Trainer package validation | ~5s |
| **Total CI wall-clock** | **~12–15 min** |

## Impact

- A single developer waiting for CI before merging spends 12–15 minutes per commit.
- During iterative fixes (typical in stabilization cycles), repeated commits can consume a large part of the workday in CI wait time.
- Discourages small, frequent commits; incentivizes batching changes.

## Backend General Tests Duration

The bottleneck is the backend certification-core suite: `~540s` (certification core + general tests combined). This includes both SQLite-backed contract tests and integration tests.

## Scale Risk

The current single-pipeline model does not scale to the platform's target architecture:

- **10 trainers**: Pipeline duration unchanged (only one trainer package exists today). No regression yet.
- **100 trainers**: Without path-filtered or matrix builds, test time grows proportionally to trainer count, pushing CI beyond 60+ minutes.
- **1000 trainers**: Impossible under the current model. A full matrix run would exceed GitHub Actions time limits.

The design must evolve to a tiered model (platform-core → per-trainer contract → affected-only triggers → nightly full matrix) before multi-trainer onboarding begins.

## Status

| Field | Value |
|-------|-------|
| Recorded | 2026-06-08 |
| Fixed in this task | **No** — documented as architecture debt only |
| Performance redesign | Deferred to dedicated architecture layer |

## Recommended Next Architecture Layer

**TRAINER-PLATFORM-CI-FEEDBACK-LOOP-FAST-PATH-AND-MULTI-TRAINER-SCALING-005** should:

1. Implement `pytest-xdist` for parallel backend test execution where safe (SQLite tests).
2. Introduce path-filtered triggers in `.github/workflows/ci.yml` so that frontend-only changes skip backend tests.
3. Design and implement the tiered matrix model (platform-core → per-trainer → affected-only → nightly).
4. Consider caching strategies for pip and npm to reduce install time.
5. Evaluate GitHub Actions larger runners or self-hosted runners for the certification core suite.
