# 004C Multi-Trainer CI Scaling Plan

## Current State

The platform currently supports 1 trainer product (QA Engineer Interview Trainer) with a single CI pipeline.

## Future CI Model

As the platform grows to support N trainers, the CI pipeline should evolve into a matrix:

### Tier 1: Platform Core Tests (every push)

```
backend core tests (SQLite + PostgreSQL)
frontend build + tests
trainer package schema validation
```

These run on every push and must complete in <15 minutes.

### Tier 2: Trainer Package Contract Tests (per-trainer)

```
for each modified trainer_packages/<trainer>/:
  - validate package structure
  - run scenario parsing tests
  - run rubric pack validation
  - smoke test with in-memory database
```

Run only for affected trainers (detected via path filter).

### Tier 3: Affected-Only Tests

```
if backend/app/ is modified:
  - run full backend suite
  
if frontend/src/ is modified:
  - run frontend full suite
  
if trainer_packages/ is modified:
  - run affected trainer package validation
```

### Tier 4: Nightly Full Matrix

```
nightly cron schedule:
  - all trainers (N x train_package validation)
  - full backend suite
  - full frontend suite
  - E2E journey for every trainer
  - PostgreSQL migration upgrade/downgrade cycle
```

## Path Filter Strategy

```yaml
on:
  push:
    paths:
      - "backend/**"
      - "frontend/**"
      - "trainer_packages/**"
      - ".github/workflows/ci.yml"
```

## Recommended GitHub Actions Matrix

```yaml
strategy:
  matrix:
    trainer: [qa_engineer_interview_trainer, business_analyst_interview_trainer]
```

Only for the nightly full matrix, not per-push.

## Parallelism Safety

- pytest-xdist is safe for SQLite tests (file-per-test)
- PostgreSQL tests require serial execution (shared database)
- Frontend tests and build are already fast (single runner)

## CI Budget Estimate

| Tier | Approx. duration | Frequency | Daily budget |
|------|-----------------|-----------|-------------|
| Platform core | 15 min | per push (assume 10) | 150 min |
| Package contract | 2 min/trainer | per push (assume 3 trainers) | 6 min |
| Affected-only | 15 min | per push (assume 5) | 75 min |
| Nightly full | 30 min | 1x daily | 30 min |
| **Total** | | | **~260 min/day** |

Well within GitHub Actions free tier (2000 min/month for Linux = ~66 min/day) or entry-level Team plan.
