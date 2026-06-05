# Known Issues - MVP-005B Railway Redeploy and Progress Resmoke

## Status

No open MVP-005B acceptance blockers remain.

## Resolved

### 1. Progress Update Not Active on Railway

**Status**: RESOLVED

The progress-update-after-evaluation fix is active on Railway after backend deployment `a8c4dd82-2764-43c9-adab-0de1cd71a5ef`.

Evidence:

```json
{
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 1,
  "progress_average_score_after_evaluation": 89.0,
  "progress_verified_on_railway": true
}
```

### 2. Backend Redeploy Path

**Status**: RESOLVED_WITH_NOTE

Deploying the backend from the repository root failed because Railway attempted a root-level Nixpacks build. The successful method was:

```text
railway up . --path-as-root --service backend --environment staging
```

Run this command from the `backend/` directory when uploading the backend service manually.

### 3. Analytics Recheck

**Status**: VERIFIED

The `evaluation_result_viewed` event was recorded, and raw-answer privacy behavior remains covered by the analytics sanitizer and local privacy tests.

## Remaining Notes

- Railway deployment metadata did not expose a git commit hash directly; proof uses deployment ID plus behavioral verification.
- Real OpenAI is still not allowed.
- Production acceptance and release allowance remain false.
