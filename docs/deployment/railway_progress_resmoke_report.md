# Railway Progress Resmoke Report - MVP-005B

## Layer
TRAINER-PLATFORM-MVP-005B-RAILWAY-REDEPLOY-AND-PROGRESS-RESMOKE

## Date
2026-06-05

## Objective
Verify that Railway external staging runs the MVP-005 progress-update-after-evaluation fix from commit `0d4e6b5` or later, and confirm that progress updates after an evaluated attempt.

## Railway Deployment Verification

| Item | Result |
|---|---|
| Backend URL | `https://backend-staging-0487.up.railway.app` |
| Frontend URL | `https://frontend-staging-4146.up.railway.app` |
| Expected fix commit | `0d4e6b5` |
| Latest source commit before redeploy | `dcf424e` |
| Initial backend deployment observed | `674bf09c-c687-4d3e-b1ce-0980ad0864e3` |
| Initial frontend deployment observed | `602d1e51-2ced-44ea-9ca7-8b71cd7bd527` |
| Root-level backend upload attempt | `f884ed4c-f6d7-41d6-bb7e-e5265616c48c` - failed because Railway tried Nixpacks against the repository root |
| Corrected backend redeploy | `a8c4dd82-2764-43c9-adab-0de1cd71a5ef` |
| Corrected backend redeploy status | SUCCESS |
| Deployment method | `railway up . --path-as-root --service backend --environment staging` from `backend/` |

Railway deployment metadata did not expose a git commit hash directly. The accepted proof is therefore a combination of:

- local source history containing the MVP-005 progress fix after `0d4e6b5`;
- successful backend upload from the local `backend/` directory;
- Railway deployment `a8c4dd82-2764-43c9-adab-0de1cd71a5ef` reaching SUCCESS;
- behavioral smoke proof showing progress now updates on external staging.

## External Checks

| Check | Result |
|---|---|
| Frontend reachable | PASS - HTTP 200 |
| Backend `/health` | PASS - `{"status":"ok","app":"TrainerPlatform","version":"0.1.0"}` |
| Backend `/ready` | PASS - `{"status":"ok","database":"ok"}` |
| Backend `/openapi.json` | PASS - HTTP 200, OpenAPI document available |

## Progress Resmoke

Fresh synthetic user:

```text
smoke-test-mvp005b-1780676751@trainerplatform.com
```

Smoke result:

| Step | Result |
|---|---|
| Registration | PASS - 201, access token returned |
| Login | PASS - 200, access token returned |
| Domain catalog | PASS - 1 domain |
| IT domain | PASS |
| QA Engineer Interview Trainer | PASS - 5 scenarios |
| Enrollment | PASS - enrolled |
| Bug Report scenario start | PASS |
| Answer submission | PASS |
| Session completion | PASS |
| Mock evaluation | PASS - score 89, passed true |
| Evaluation result fetch | PASS |
| Progress after evaluation | PASS - total_attempts 1, completed_scenarios 1, average_score 89.0 |

## Analytics Recheck

| Check | Result |
|---|---|
| `evaluation_result_viewed` event | PASS - `status=recorded` |
| Raw-answer privacy POST | PASS - `status=recorded`; raw answer keys are sanitized by server-side allowlist/blocklist rules |
| MVP-005 analytics classification | Still valid |

## Quality Checks

| Check | Result |
|---|---|
| Backend tests | PASS - 66 passed, 3 skipped |
| Frontend build | PASS |
| Frontend tests | PASS - 10 passed |
| Trainer package validation | PASS |
| OpenAPI export | PASS - 24 paths |

## Verdict

```json
{
  "TRAINER_PLATFORM_MVP_005B": "ACCEPTED",
  "TRAINER_PLATFORM_MVP_005": "FULLY_ACCEPTED",
  "external_staging": "HARDENED",
  "progress_verified_on_railway": true,
  "analytics_verified_or_classified": true,
  "real_openai": "NOT_ALLOWED_YET",
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": "real_openai_staging_gate"
}
```
