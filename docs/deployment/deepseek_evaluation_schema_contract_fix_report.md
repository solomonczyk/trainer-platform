# DeepSeek Evaluation Schema Contract Fix Report

## Layer
TRAINER-PLATFORM-MVP-006C-FIX-DEEPSEEK-EVALUATION-SCHEMA-CONTRACT

## Date
2026-06-05

## Verdict
ACCEPTED

## Summary

MVP-006C fixes the DeepSeek evaluation schema contract so real DeepSeek staging evaluations normalize to the canonical evaluation schema and return `validation_status=validated` instead of `partial`.

The backend was redeployed to Railway staging and a synthetic real DeepSeek smoke passed with `ai_model_used=deepseek-v4-flash`, valid non-empty criteria, score returned, passed boolean returned, no exposed `reasoning_content`, progress update verified, and privacy-safe analytics verified.

## Problem

DeepSeek v4-flash can return evaluation results with provider-specific shape differences:

1. Alternative field names, such as `id` instead of `criterion_id`.
2. Evidence-like content under `reasoning`, `justification`, or similar fields.
3. Missing `comment` or `improvement` fields.
4. Missing or empty criteria arrays.
5. Dict-keyed criteria instead of a criteria array.
6. `reasoning_content` in the OpenAI-compatible response message.

These variations can cause `validate_evaluation_output()` to add validation errors, which turns a real provider success into `validation_status=partial`.

## Fix

`OpenAIProviderAdapter` now applies a DeepSeek-only, rubric-aware normalization step after parsing the provider response.

| Area | Fix |
|---|---|
| Criteria shape | Normalizes criteria arrays and dict-keyed criteria |
| Criterion IDs | Maps `criterion_id`, `id`, `criteria_id`, and `criterionId` |
| Rubric alignment | Fills missing rubric criteria and filters provider extras when a rubric is present |
| Evidence | Maps `evidence`, `evidences`, `justification`, and `reasoning`; supplies safe default evidence when missing |
| Score | Normalizes `overall_score`, `score`, `overallScore`, and `total_score`; clamps scores to 0-100 |
| Passed | Ensures boolean `passed`, deriving from score when omitted |
| Feedback | Builds a safe `feedback` field from available criterion details |
| Reasoning content | Uses `reasoning_content` only as parse input when needed, then strips it from normalized output |
| Safety | Ensures list fields and confidence values are schema-safe |

## Files Changed

| File | Change |
|---|---|
| `backend/app/ai_gateway/adapters/openai_adapter.py` | Added DeepSeek-only schema normalization and reasoning-content handling |
| `backend/tests/test_ai_gateway.py` | Added DeepSeek normalization and validator contract tests |

## Tests

| Check | Result |
|---|---|
| AI Gateway tests | PASS - 50 passed |
| DeepSeek schema contract tests | PASS |
| Full backend tests | PASS - 105 passed, 3 skipped |
| OpenAPI export | PASS - 24 paths |
| Trainer package validation | PASS |
| Frontend provider secret scan | PASS - no matches |

## Staging Deployment

| Field | Value |
|---|---|
| Railway project | `800b800a-c306-4bcb-aa81-bad8db9e51fc` |
| Service | `backend` |
| Environment | `staging` |
| Deployment ID | `0fea54f7-77ae-4239-9b9b-82047c25973e` |
| Deployment status | `SUCCESS` |

## Real DeepSeek Smoke Evidence

```json
{
  "synthetic_user_only": true,
  "ai_model_used": "deepseek-v4-flash",
  "validation_status": "validated",
  "criteria_schema_valid": true,
  "criteria_count": 1,
  "reasoning_content_exposed": false,
  "overall_score": 100,
  "passed": true,
  "ai_latency_ms": 4859,
  "ai_cost_usd": 0.001,
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 1,
  "progress_average_score_after_evaluation": 100.0,
  "analytics_raw_answer_echoed": false
}
```

## Forbidden Actions Check

```json
{
  "openai_enabled": false,
  "openai_api_key_added": false,
  "deepseek_key_exposed": false,
  "frontend_provider_secrets_configured": false,
  "production_deployed": false,
  "production_accepted": false,
  "release_allowed": false,
  "new_trainers_added": false,
  "payments_added": false,
  "market_launch": false
}
```

