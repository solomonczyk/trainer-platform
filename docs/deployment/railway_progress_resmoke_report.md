# Railway Progress Resmoke Report — MVP-005B

## Layer
TRAINER-PLATFORM-MVP-005B-RAILWAY-REDEPLOY-AND-PROGRESS-RESMOKE

## Date
2026-06-05

## Objective
Verify that Railway external staging runs the MVP-005 progress-update-after-evaluation fix (commits `d27b537` or later).

## Method

### 1. Local Code Verification
- Commit `d27b537` adds `ProgressService.update_progress_after_evaluation()` call in `EvaluationService.evaluate_attempt()` (backend/app/modules/evaluations/service.py lines 178-198)
- Local backend test `test_progress_updated_after_evaluation` passes (verifies total_attempts >= 1, average_score > 0)
- Latest commit: `463d1ee` (empty trigger commit), parent: `0d4e6b5`

### 2. Railway Deployment State
- **Railway CLI**: Not authenticated — `railway login` requires interactive terminal
- **Railway API**: Project token is available but has limited scope (deployment environment use only, not CLI auth)
- **Push to GitHub**: Commit `463d1ee` pushed to `origin/master` to trigger Railway auto-deploy (if configured)
- **Auto-deploy status**: Unknown — no webhook verification possible without GitHub API auth

### 3. Behavioral Verification
Full smoke test run against Railway staging:

| Step | Result |
|------|--------|
| Frontend reachable | ✅ HTTP 200 |
| Backend health | ✅ `{"status":"ok"}` |
| Register synthetic user | ✅ 201 |
| Login | ✅ 200, token received |
| Enroll in QA Trainer | ✅ 201, enrolled |
| Start Bug Report scenario | ✅ session + attempt created |
| Submit answer | ✅ 200 |
| Complete attempt | ✅ 200 |
| Evaluate attempt | ✅ 200, mock AI evaluation complete |
| Score returned | ✅ 43–91 (mock AI, varies by answer) |
| Progress (total_attempts) | ❌ **0** (expected >= 1) |
| Progress (average_score) | ❌ **0.0** (expected > 0) |
| Progress (completed_scenarios) | ❌ **0** |

### 4. Diagnosis
**Root cause**: Railway external staging is still running the **pre-fix code**. The MVP-005 progress update fix was committed in `d27b537` but has NOT been deployed to Railway.

Evidence:
1. Evaluation completes successfully (mock AI returns scores)
2. Progress endpoint returns 0 attempts in all smoke test runs (3 independent runs)
3. Code analysis confirms `update_progress_after_evaluation()` is wired but only activated on deployment

### 5. Deploy Attempt
Action taken:
- Empty commit `463d1ee` pushed to `origin master` to trigger Railway GitHub auto-deploy
- Result: Railway endpoints remained healthy but progress fix still inactive after 10+ minutes

**Conclusion**: Either Railway auto-deploy is not configured, or the GitHub integration requires additional setup.

## Required Operator Action
```
NEEDS_OPERATOR_ACTION

To complete the deployment:
1. Authenticate Railway CLI: railway login
2. Redeploy backend: railway up --service backend -e staging --detach
3. Verify deployment completes
4. Re-run smoke test
```

## Current State Summary
```
railway_running_mvp005_fix: false
progress_verified_on_railway: false
external_smoke_test_passed: false (progress step fails)
analytics_verified: true (classification from MVP-005 still valid)
real_openai_enabled: false
production_accepted: false
release_allowed: false
next_allowed_action: operator_railway_redeploy
```
