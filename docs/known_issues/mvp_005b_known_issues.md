# Known Issues - MVP-005B Railway Redeploy and Progress Resmoke

## Status

No open MVP-005B acceptance blockers remain.

## Resolved

### 1. Progress Update Not Active on Railway

**Status**: RESOLVED

The progress-update-after-evaluation fix is active on Railway after backend deployment `a48cd8e6-b7db-424d-80fe-691f57f5612b`.

Evidence:

```json
{
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 0,
  "progress_average_score_after_evaluation": 51.0,
  "progress_verified_on_railway": true
}
```

Note: `completed_scenarios=0` because the evaluation `passed=false` (score 51 below threshold). This is correct behavior — scenarios increment only on pass.

### 2. Railway Build Root Directory

**Status**: RESOLVED_WITH_NOTE

The `railway.json` has correct service-level root directories (`"root": "backend"` and `"root": "frontend"`). When deploying via `railway up`, the `--path-as-root` flag must be used from the service directory to ensure correct build context.

Successful deployment commands:

```bash
# From backend/ directory:
railway up . --path-as-root --service backend --environment staging --detach --json

# From frontend/ directory:
railway up . --path-as-root --service frontend --environment staging --detach --json
```

### 3. Analytics Recheck

**Status**: VERIFIED

The `evaluation_result_viewed` event was recorded (`status=recorded`), and raw-answer privacy behavior is verified — the server returned `status=skipped` for raw answer analytics events.

### 4. Scenario Start Requires scenario_id (Text Key), Not UUID

**Status**: DOCUMENTED

The `/api/v1/scenarios/{scenario_id}/start` endpoint expects the textual `scenario_id` field (e.g., `qa_bug_report_structure_v1`), not the UUID `id` field from the scenarios list. Using the UUID returns 404 "Scenario not found".

## Remaining Notes

- Railway deployment metadata does not expose a git commit hash directly; proof uses deployment ID plus behavioral verification.
- Real OpenAI is still not allowed.
- Production acceptance and release allowance remain false.
- Enroll endpoint requires `json={}` (empty JSON body) for full product enrollment; no-body POST returns 201 but may not activate scenario access in some cases.
