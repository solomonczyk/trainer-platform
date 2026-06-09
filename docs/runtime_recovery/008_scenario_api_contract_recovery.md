# 008 — Scenario API Contract Recovery

## Issue

Frontend was unable to load scenario data from backend on Railway staging,
resulting in 404 errors for scenario list and detail endpoints.

## API Route Contract

### Frontend Client Routes (lib/api/client.ts)

| Method | Path | Frontend Function |
|--------|------|-------------------|
| GET | `/api/v1/trainers/{slug}/scenarios` | `getTrainerScenarios()` |
| GET | `/api/v1/scenarios/{id}` | `getScenario()` |
| POST | `/api/v1/scenarios/{id}/start` | `startScenario()` |
| POST | `/api/v1/sessions/{id}/messages` | `submitMessage()` |
| POST | `/api/v1/sessions/{id}/complete` | `completeSession()` |
| POST | `/api/v1/attempts/{id}/evaluate` | `evaluateAttempt()` |
| GET | `/api/v1/attempts/{id}/evaluation` | `getEvaluation()` |

### Backend Routes (app/modules/scenarios/router.py)

| Method | Path | Handler |
|--------|------|---------|
| GET | `/api/v1/trainers/{trainer_slug}/scenarios` | `list_scenarios_for_trainer()` |
| GET | `/api/v1/scenarios/{scenario_id}` | `get_scenario_detail()` |

### Route Table Alignment

Frontend and backend route contracts are aligned. Both use:

- Base path: `/api/v1`
- Trainer slug in path: yes
- Scenario ID in path: yes
- No trailing-slash dependency: both sides clean

## Configuration Dependency

The frontend API client resolves base URL from:

```javascript
process.env.NEXT_PUBLIC_API_BASE_URL  // canonical
process.env.NEXT_PUBLIC_API_URL       // backward-compat fallback
```

On Railway staging, this must be set to the backend external URL
(e.g., `https://backend-staging-XXXX.up.railway.app`).

## Verification

Runtime tests pass against local backend (SQLite):
- `test_scenario_runtime.py` — 7/7 passed
- `test_domain_trainer_catalog.py` — 5/5 passed
- `test_ba_phase2.py` — 10/10 passed
- `test_evaluation_runtime.py` — 4/4 passed

## Root Cause

The 404 error observed on Railway staging is a deployment configuration issue
(`NEXT_PUBLIC_API_BASE_URL` not set or pointing at wrong URL), not a code-level
route mismatch. The frontend API client correctly logs a fatal error when
the env var is missing in non-development environments.
