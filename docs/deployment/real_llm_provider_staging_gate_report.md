# Real LLM Provider Staging Gate Report - MVP-006

## Layer
TRAINER-PLATFORM-MVP-006-DEEPSEEK-V4-FLASH-STAGING-GATE

## Date
2026-06-05

## Selected Provider
DeepSeek

## Verdict
ACCEPTED_FOR_STAGING_REAL_PROVIDER_GATE

## Summary
Railway staging backend variables for DeepSeek are present, and `OPENAI_API_KEY` remains absent. The backend AI Gateway now maps the provider-neutral MVP-006 variables into the OpenAI-compatible DeepSeek adapter.

A controlled synthetic staging smoke was executed after redeploy. The evaluation response reported `ai_model_used=deepseek-v4-flash`, returned `validation_status=validated`, produced a structured score, updated progress, and accepted a privacy-safe analytics event.

No provider secret values were printed, copied, committed, or stored in documentation.

## Required Railway Staging Backend Variables

```text
DEEPSEEK_API_KEY: secret only
AI_PROVIDER=deepseek
AI_REAL_PROVIDER_ENABLED=true
AI_MODEL_EVALUATOR=deepseek-v4-flash
AI_PROVIDER_BASE_URL=https://api.deepseek.com
AI_MAX_COST_PER_REQUEST_USD=0.05
AI_TIMEOUT_SECONDS=30
AI_FALLBACK_PROVIDER=mock
AI_EVALUATION_JSON_SCHEMA_REQUIRED=true
```

## Variable Presence Check

Values were redacted; only variable names were checked.

| Variable | Present in Railway staging backend | Notes |
|---|---:|---|
| `DEEPSEEK_API_KEY` | true | Required operator secret present |
| `AI_PROVIDER` | true | Expected `deepseek` |
| `AI_REAL_PROVIDER_ENABLED` | true | Expected `true` in staging only |
| `AI_MODEL_EVALUATOR` | true | Expected `deepseek-v4-flash` |
| `AI_PROVIDER_BASE_URL` | true | Expected `https://api.deepseek.com` |
| `AI_MAX_COST_PER_REQUEST_USD` | true | Expected `0.05` |
| `AI_TIMEOUT_SECONDS` | true | Expected `30` |
| `AI_FALLBACK_PROVIDER` | true | Expected `mock` |
| `AI_EVALUATION_JSON_SCHEMA_REQUIRED` | true | Expected `true` |
| `OPENAI_API_KEY` | false | Must remain absent for this gate |

## Provider Validation

| Check | Result |
|---|---|
| OpenAI absent | PASS |
| DeepSeek variables present | PASS |
| Backend AI Gateway path used | PASS |
| Frontend direct provider calls | PASS - none found |
| Real DeepSeek model observed | PASS - response reported `deepseek-v4-flash` |
| Structured evaluation schema | PASS |
| Progress after evaluation | PASS |
| Analytics privacy event path | PASS |

## Runtime Mapping Result

The backend AI Gateway resolves `AI_PROVIDER=deepseek`, `AI_MODEL_EVALUATOR=deepseek-v4-flash`, `AI_PROVIDER_BASE_URL=https://api.deepseek.com`, `AI_TIMEOUT_SECONDS=30`, and `DEEPSEEK_API_KEY` from Railway staging backend environment. The adapter reported provider `deepseek`, model `deepseek-v4-flash`, and the DeepSeek base URL during sanitized validation.

## Smoke Evidence

```json
{
  "synthetic_user_only": true,
  "ai_model_used": "deepseek-v4-flash",
  "expected_model": "deepseek-v4-flash",
  "deepseek_model_observed": true,
  "openai_fallback_absent": true,
  "overall_score": 88,
  "passed": true,
  "validation_status": "validated",
  "criteria_count": 3,
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 1,
  "progress_average_score_after_evaluation": 88.0,
  "analytics_status": "recorded"
}
```

## Forbidden Actions Check

```json
{
  "openai_configured": false,
  "openai_enabled": false,
  "deepseek_key_exposed": false,
  "deepseek_key_committed": false,
  "frontend_provider_secrets_configured": false,
  "production_deployed": false,
  "production_accepted": false,
  "release_allowed": false
}
```

## Next Allowed Action

```text
controlled_beta_readiness_after_deepseek_staging_gate_evidence_review
```
