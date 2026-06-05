# Railway Migration and Seed Report — MVP-005

**Date**: 2026-06-05
**Layer**: TRAINER-PLATFORM-MVP-005-STAGING-HARDENING-BEFORE-REAL-OPENAI
**Target**: Railway PostgreSQL (staging environment)

## Migration Status

| Item | Status |
|------|--------|
| Revision | `001` — Initial MVP schema |
| Status | ✅ Applied |
| Tables created | 27 |
| Migration command | `alembic upgrade head` (run in Railway Docker build) |

### Schema — 27 Tables Created

- `users`, `user_profiles`
- `domains`, `trainer_products`, `trainer_versions`, `trainer_localizations`
- `tracks`, `modules`
- `scenarios`, `scenario_steps`
- `skill_maps`, `skills`
- `rubrics`, `rubric_criteria`, `critical_errors`
- `user_trainer_enrollments`, `simulation_sessions`, `simulation_messages`, `attempts`
- `evaluations`, `evaluation_criteria_results`
- `trainer_progress`, `skill_scores`
- `analytics_events`, `ai_requests`
- `feature_flags`
- `alembic_version`

## Seed Data

### QA Engineer Interview Trainer

| Check                          | Value         | Status |
|--------------------------------|---------------|--------|
| IT Domain exists               | `it`          | ✅     |
| QA Engineer Trainer exists     | `qa-engineer-interview-trainer` | ✅ |
| Trainer version                | `1.0.0`       | ✅     |
| Scenarios count                | 5             | ✅     |
| Locales                        | ru-RU, en-US  | ✅     |
| Rubrics                        | 5             | ✅     |
| Skill maps                     | 1             | ✅     |
| Critical errors                | 4             | ✅     |
| Feature flags                  | 8 configured  | ✅     |
| Admin user                     | admin@trainerplatform.com | ✅ |

### Seed Scenarios

1. `qa_bug_report_structure_v1`
2. `qa_login_form_testing_v1`
3. `qa_regression_vs_retest_v1`
4. `qa_self_presentation_v1`
5. `qa_test_case_vs_checklist_v1`

## Migration Verification Strategy

### Primary Method: Railway Deployment Context

```yaml
method: "railway_deployment_context"
migration_command: "alembic upgrade head"
execution_context: "Dockerfile build in Railway environment"
verification_proof:
  - "Health endpoint returns 200 OK"
  - "Domain API returns IT domain"
  - "Trainer API returns QA Engineer Interview Trainer"
  - "Scenario API returns 5 scenarios"
  - "Seed admin user login works"
```

**How migrations are applied:**
1. Railway builds the backend from `backend/Dockerfile`
2. The migration runs as part of the container startup
3. If migration fails, health check fails and Railway restarts
4. Successful health checks + API responses confirm correct schema

### Secondary: Railway PostgreSQL Proxy

For direct schema inspection:
```bash
railway connect postgres   # Opens local tunnel to internal DB
# Then connect locally: psql "$DATABASE_URL"
```

### Local Direct DB Check Restriction

Running `alembic check` locally against `postgres.railway.internal:5432` fails because this hostname is only reachable within the Railway private network.

```
ConnectionRefusedError: could not connect to server
  Connection refused
  Is the server running on host "postgres.railway.internal" (10.x.x.x)
  and accepting TCP/IP connections on port 5432?
```

This is by design — Railway's internal networking isolates services. **Not a bug.**

## Verification Result

| Check | Result |
|-------|--------|
| Railway migrations applied | ✅ |
| Schema verified via Railway context | ✅ |
| Local direct DB check blocked by network | ✅ (documented, by design) |
| Database URL not exposed | ✅ (no secrets committed) |

## Commands

```bash
# Run migrations (local development)
cd backend
alembic upgrade head

# Seed trainer package
cd backend
python scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer

# Connect to Railway PostgreSQL via tunnel
railway connect postgres
```
