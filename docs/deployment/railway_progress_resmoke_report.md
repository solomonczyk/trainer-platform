# Railway Progress Resmoke Report - MVP-005B

## Layer
TRAINER-PLATFORM-MVP-005B-FIX-RAILWAY-ROOT-DIRECTORY-AND-REDEPLOY

## Date
2026-06-05

## Objective
Verify that Railway external staging runs the MVP-005 progress-update-after-evaluation fix and that progress updates correctly after an evaluated attempt.

## Railway Deployment Verification

| Item | Result |
|---|---|
| Backend URL | `https://backend-staging-0487.up.railway.app` |
| Frontend URL | `https://frontend-staging-4146.up.railway.app` |
| Backend deployment ID | `a48cd8e6-b7db-424d-80fe-691f57f5612b` |
| Backend deployment status | SUCCESS |
| Frontend deployment ID | `39c27d96-45e1-4db9-841b-dc2ef72cdaab` |
| Frontend deployment status | SUCCESS |
| Deployment method | `railway up . --path-as-root --service <name> --environment staging` from service directories |
| Root directory fix | Confirmed - railway.json has `"root": "backend"` and `"root": "frontend"`; deployments use `--path-as-root` |

## External Checks

| Check | Result |
|---|---|
| Frontend reachable | PASS - HTTP 200 |
| Backend `/health` | PASS - `{"status":"ok","app":"TrainerPlatform","version":"0.1.0"}` |
| Backend `/ready` | PASS - `{"status":"ok","database":"ok"}` |
| Backend `/openapi.json` | PASS - HTTP 200, 24 paths |

## Progress Resmoke

Fresh synthetic user:

```text
smoke-test-mvp005b-fix-2a7a2487@trainerplatform.com
```

Smoke result:

| Step | Result |
|---|---|
| Registration | PASS - 201, access token returned |
| Domain catalog | PASS - 1 domain |
| IT domain | PASS |
| QA Engineer Interview Trainer | PASS - 5 scenarios |
| Enrollment | PASS - enrolled |
| Bug Report scenario start | PASS (using `scenario_id=qa_bug_report_structure_v1`) |
| Answer submission | PASS |
| Session completion | PASS |
| Mock evaluation | PASS - score 51, passed false |
| Evaluation result fetch | PASS |
| Progress after evaluation | PASS - total_attempts 1, average_score 51.0 |

## Analytics Recheck

| Check | Result |
|---|---|
| `evaluation_result_viewed` event | PASS - `status=recorded` |
| Raw-answer privacy | PASS - `status=skipped`; server refused to store raw answer content |
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
  "railway_build_root_fixed": true,
  "progress_verified_on_railway": true,
  "analytics_verified_or_classified": true,
  "real_openai": "NOT_ALLOWED_YET",
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": "real_openai_staging_gate"
}
```
