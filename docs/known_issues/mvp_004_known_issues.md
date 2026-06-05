# MVP-004 Known Issues

## 1. Progress Not Auto-Updated After Evaluation

**Severity**: Low
**Component**: `backend/app/modules/evaluations/service.py`
**Description**: After `evaluate_attempt` completes successfully, the progress service is not called to update the user's progress. The `update_progress_after_evaluation` method exists in `ProgressService` but is not invoked from the evaluation flow.
**Impact**: User progress shows 0 attempts even after completing scenarios and receiving evaluations.
**Workaround**: Progress can be manually updated via the admin panel.
**Fix**: Call `ProgressService.update_progress_after_evaluation()` from `EvaluationService.evaluate_attempt()` after saving the evaluation.

## 2. Analytics Events Return "skipped"

**Severity**: Low
**Component**: `backend/app/modules/analytics`
**Description**: The `POST /api/v1/analytics/events` endpoint returns `{"status": "skipped"}` for analytics events. This may be due to a feature flag check or filtering in the analytics service.
**Impact**: Analytics events are not recorded in the database.
**Workaround**: None currently.
**Fix**: Investigate analytics service logic to determine why events are skipped.

## 3. Alembic Check Fails Locally Against Railway DB

**Severity**: Low
**Component**: `backend/app/db/migrations`
**Description**: Running `alembic check` locally fails with `ConnectionRefusedError` because the Railway PostgreSQL uses an internal hostname (`postgres.railway.internal`) that is only accessible within the Railway network.
**Impact**: Cannot verify migration state from local development environment.
**Workaround**: Use the public Railway PostgreSQL URL with `alembic check` or run the check from within a Railway deployment.
**Fix**: This is inherent to Railway's internal networking — not a code bug.

## 4. Frontend Localhost Fallback in API Client

**Severity**: Low
**Component**: `frontend/src/lib/api/client.ts`
**Description**: The API client has `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"` as a fallback. In staging builds with the correct env var set, this is overridden.
**Impact**: None for staging (env var is set). Could cause confusion if env var is missing in a future deployment.
**Fix**: Remove the fallback or make it a staging-specific URL.
