# Railway External Staging Smoke Test Report - MVP-005B

## Test Run

**Date**: 2026-06-05  
**Layer**: TRAINER-PLATFORM-MVP-005B-FIX-RAILWAY-ROOT-DIRECTORY-AND-REDEPLOY  
**Tester**: Automated API smoke with synthetic user

## Environment

| Parameter | Value |
|---|---|
| Backend URL | `https://backend-staging-0487.up.railway.app` |
| Frontend URL | `https://frontend-staging-4146.up.railway.app` |
| AI provider | mock adapter; real OpenAI remains disabled |
| Backend deployment | `a48cd8e6-b7db-424d-80fe-691f57f5612b` |
| Frontend deployment | `39c27d96-45e1-4db9-841b-dc2ef72cdaab` |
| Deployment method | `railway up . --path-as-root --service <name> --environment staging` |

## Test Flow Results

| # | Step | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Frontend reachable | HTTP 200 | 200 | PASS |
| 2 | Backend health | `status=ok` | ok | PASS |
| 3 | Backend ready | `database=ok` | ok | PASS |
| 4 | OpenAPI available | HTTP 200 | 200 | PASS |
| 5 | User registration | token returned | 201, token returned | PASS |
| 6 | Domain catalog | at least 1 domain | 1 domain | PASS |
| 7 | IT domain detail | `slug=it` | found | PASS |
| 8 | Trainer detail | QA Trainer visible | 5 scenarios | PASS |
| 9 | Enrollment | enrolled | enrolled | PASS |
| 10 | Start Bug Report scenario | session + attempt | created (using `scenario_id`) | PASS |
| 11 | Submit answer | message accepted | accepted | PASS |
| 12 | Complete session | attempt completed | completed | PASS |
| 13 | Mock AI evaluation | score > 0 | score 51 | PASS |
| 14 | Evaluation result | score returned | score 51 | PASS |
| 15 | Progress after evaluation | total_attempts >= 1 | total_attempts 1 | PASS |
| 16 | Progress average score | average_score > 0 | average_score 51.0 | PASS |
| 17 | Analytics event | recorded or classified | recorded | PASS |
| 18 | Raw-answer privacy check | no raw answer persistence | server skipped event | PASS |

## Summary

- Passed: 18/18 checks
- Failed: 0/18 checks
- Progress is verified on Railway external staging.
- Railway build root directory is fixed (services deployed from correct directories).
- MVP-005B blocker is cleared.

## Verdict

**PASSED** - Railway external staging is hardened for MVP-005B, progress updates after evaluation, and build root directory is correctly configured.

```json
{
  "TRAINER_PLATFORM_MVP_005B": "ACCEPTED",
  "external_staging": "HARDENED",
  "progress_verified_on_railway": true,
  "railway_build_root_fixed": true,
  "next_allowed_action": "real_openai_staging_gate"
}
```
