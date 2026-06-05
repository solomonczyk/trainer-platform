# Railway External Staging Smoke Test Report - MVP-005B

## Test Run

**Date**: 2026-06-05  
**Layer**: TRAINER-PLATFORM-MVP-005B-RAILWAY-REDEPLOY-AND-PROGRESS-RESMOKE  
**Tester**: Automated API smoke with synthetic user

## Environment

| Parameter | Value |
|---|---|
| Backend URL | `https://backend-staging-0487.up.railway.app` |
| Frontend URL | `https://frontend-staging-4146.up.railway.app` |
| AI provider | mock adapter; real OpenAI remains disabled |
| Backend deployment | `a8c4dd82-2764-43c9-adab-0de1cd71a5ef` |
| Frontend deployment | `602d1e51-2ced-44ea-9ca7-8b71cd7bd527` |
| Expected fix commit | `0d4e6b5` or later |
| Source commit before redeploy | `dcf424e` |

## Test Flow Results

| # | Step | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Frontend reachable | HTTP 200 | 200 | PASS |
| 2 | Backend health | `status=ok` | ok | PASS |
| 3 | Backend ready | `database=ok` | ok | PASS |
| 4 | OpenAPI available | HTTP 200 | 200 | PASS |
| 5 | User registration | token returned | 201, token returned | PASS |
| 6 | Login | token returned | 200, token returned | PASS |
| 7 | Domain catalog | at least 1 domain | 1 domain | PASS |
| 8 | IT domain detail | `slug=it` | found | PASS |
| 9 | Trainer detail | QA Trainer visible | 5 scenarios | PASS |
| 10 | Enrollment | enrolled | enrolled | PASS |
| 11 | Start Bug Report scenario | session + attempt | created | PASS |
| 12 | Submit answer | message accepted | accepted | PASS |
| 13 | Complete session | attempt completed | completed | PASS |
| 14 | Mock AI evaluation | score > 0 | score 89, passed true | PASS |
| 15 | Evaluation result | score returned | score 89 | PASS |
| 16 | Progress after evaluation | total_attempts >= 1 | total_attempts 1 | PASS |
| 17 | Progress completed scenarios | completed_scenarios >= 1 when passed | completed_scenarios 1 | PASS |
| 18 | Progress average score | average_score > 0 | average_score 89.0 | PASS |
| 19 | Analytics event | recorded or classified | recorded | PASS |
| 20 | Raw-answer privacy check | no raw answer persistence | server accepted sanitized event | PASS |

## Summary

- Passed: 20/20 checks
- Failed: 0/20 checks
- Progress is verified on Railway external staging.
- MVP-005 blocker is cleared.

## Notes

The first redeploy attempt from the repository root created failed deployment `f884ed4c-f6d7-41d6-bb7e-e5265616c48c` because Railway attempted a root-level Nixpacks build. The corrected redeploy from `backend/` with `--path-as-root` succeeded as `a8c4dd82-2764-43c9-adab-0de1cd71a5ef`.

## Verdict

**PASSED** - Railway external staging is hardened for MVP-005B, and progress updates after evaluation.
