# Railway External Staging Smoke Test Report — MVP-005B

## Test Run: 2026-06-05
**Layer**: TRAINER-PLATFORM-MVP-005B-RAILWAY-REDEPLOY-AND-PROGRESS-RESMOKE

## Environment
| Parameter         | Value                                         |
|-------------------|-----------------------------------------------|
| Backend URL       | https://backend-staging-0487.up.railway.app   |
| Frontend URL      | https://frontend-staging-4146.up.railway.app  |
| AI Provider       | mock                                          |
| Deployed commit   | Unknown (Railway CLI not authenticated)       |
| Expected fix      | Commit `d27b537` or later                     |

## Test Flow Results

| # | Step                           | Expected                       | Actual            | Status |
|---|--------------------------------|--------------------------------|-------------------|--------|
| 1 | Frontend reachable             | HTTP 200                       | 200               | ✅     |
| 2 | Health check                   | `{"status": "ok"}`             | ok                | ✅     |
| 3 | Ready check                    | `{"database": "ok"}`           | ok                | ✅     |
| 4 | OpenAPI available              | HTTP 200                       | 200               | ✅     |
| 5 | User registration              | 201, token returned            | 201               | ✅     |
| 6 | Login                          | 200, access token              | 200               | ✅     |
| 7 | Domain catalog                 | >= 1 domain                    | 1 domain (IT)     | ✅     |
| 8 | IT domain detail               | trainer visible                | QA Trainer found  | ✅     |
| 9 | Trainer detail                 | 5 scenarios                    | 5 scenarios       | ✅     |
| 10| Enrollment                     | 201, enrolled                  | 201               | ✅     |
| 11| Start Bug Report scenario      | session + attempt              | session + attempt | ✅     |
| 12| Submit answer                  | 200, message accepted          | 200               | ✅     |
| 13| Complete session               | 200, status completed          | 200               | ✅     |
| 14| Mock AI evaluation             | score > 0, passed              | score=43–91       | ✅     |
| 15| Evaluation result              | overall_score present          | 43–91             | ✅     |
| 16| **Progress after evaluation**  | **total_attempts >= 1**        | **0**             | **❌** |
| 17| Analytics event recorded       | status=recorded                | recorded          | ✅     |
| 18| Raw answers absent in analytics| recorded without raw answer    | recorded          | ✅     |

## Summary
- **Passed**: 17/18 steps
- **Failed**: 1/18 (Progress update — Railway still runs pre-fix code)
- **Overall**: ⚠️ BLOCKED — requires Railway operator redeploy

## Progress Failure Detail
```
Evaluation: status=200, passed=true, score=91 (mock AI)
Progress:   total_attempts=0, average_score=0.0, completed_scenarios=0
```

This is consistent across 3 independent tests with different synthetic users. The code fix exists in `backend/app/modules/evaluations/service.py` (lines 178–198) but is not deployed to Railway.

## Required Action
1. `railway login` (interactive)
2. `railway up --service backend -e staging --detach`
3. `railway up --service frontend -e staging --detach`
4. Re-run this smoke test
