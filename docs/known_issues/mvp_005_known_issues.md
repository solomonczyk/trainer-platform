# MVP-005 Known Issues

**Layer**: TRAINER-PLATFORM-MVP-005-STAGING-HARDENING-BEFORE-REAL-OPENAI
**Date**: 2026-06-05
**Status**: HARDENED — all issues from MVP-004 resolved or formally classified

## Resolved Issues (from MVP-004)

### 1. Progress Not Auto-Updated After Evaluation

**Severity**: ~~Low~~ **RESOLVED**
**Component**: `backend/app/modules/evaluations/service.py`
**Fix**: `ProgressService.update_progress_after_evaluation()` is now called from `EvaluationService.evaluate_attempt()` after a successful evaluation. Progress is updated with `total_attempts` (+1), `completed_scenarios` (+1 if passed), rolling `average_score`, and `readiness_status` recalculation.
**Verification**: Backend test `test_progress_updated_after_evaluation` passes. Smoke test will show updated progress after Railway deployment.

### 2. Analytics Events Return "skipped"

**Severity**: ~~Low~~ **RESOLVED**
**Component**: Backend `app/modules/analytics/service.py` + Frontend evaluation result page
**Classification**: **Case B — Intentional Skip** (by design)
**Why skipped**: The analytics service has three intentional skip reasons:

1. **Feature flag guard**: If `ff_analytics_enabled` is `False` (DB or settings), event is skipped.
2. **Event type allowlist**: Only 24 types in `SAFE_EVENT_TYPES` are accepted; others are silently dropped.
3. **Property sanitisation**: Values under keys `answer`, `answer_text`, `content` are stripped; credential-like values are removed; passwords/tokens/api_keys are blocked.

**Frontend fix**: Added `sendAnalyticsEvent("evaluation_result_viewed")` to the evaluation result page to fire an event when results are viewed. Backend analytics tests (5 tests) all confirm `"status": "recorded"` for valid event types.

### 3. Alembic Check Fails Locally Against Railway DB

**Severity**: ~~Low~~ **RESOLVED (formally classified)**
**Component**: Railway internal networking
**Classification**: By design — `postgres.railway.internal` is only reachable within Railway's private network.
**Verification method**: Migrations are verified via Railway deployment context (health checks, API responses confirm schema correctness). See `docs/deployment/railway_migration_and_seed_report.md`.

### 4. Frontend Localhost Fallback in API Client

**Severity**: ~~Low~~ **RESOLVED**
**Component**: `frontend/src/lib/api/client.ts`, `frontend/next.config.js`
**Fix**: Added `getApiBaseUrl()` function with environment-aware fallback:
- `NEXT_PUBLIC_API_URL` set → use it (all environments)
- URL unset + `APP_ENV=local` or `development` → fall back to `localhost:8000`
- URL unset + `APP_ENV=staging` or `production` → return `""` with loud console error
**Required env vars**: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_ENV`
**Verification**: 7 new frontend tests cover all env combinations.

## Remaining Issues

### 5. Railway Progress Update Pending Deployment

**Severity**: Low
**Component**: Railway deployment
**Description**: The progress update fix is code-verified (backend test passes) but will only take effect on Railway staging after `git push origin master` triggers an auto-deploy. The external smoke test shows `attempts=0` on the currently deployed version.
**Workaround**: Wait for Railway to rebuild and deploy from master.
**Resolution trigger**: `git push origin master` → Railway auto-deploy.

### 6. Analytics Events Only Fired from Evaluation Result Page

**Severity**: Low
**Component**: `frontend/src/app/attempts/[attemptId]/result/page.tsx`
**Description**: Analytics events are currently only sent from the evaluation result page (`evaluation_result_viewed`). Other user actions (scenario start, answer submission, enrollment) do not yet fire analytics events from the frontend.
**Impact**: Analytics coverage is partial. Backend accepts events for all 24 SAFE_EVENT_TYPES, but the frontend only sends 1.
**Fix**: Wire `sendAnalyticsEvent()` into other frontend flows (scenario start, answer submit, etc.).

## Security Notes

- No secrets committed
- Railway token not exposed
- Database URL not exposed
- Real OpenAI key not enabled
- Production acceptance: `false`
- Release allowed: `false`
