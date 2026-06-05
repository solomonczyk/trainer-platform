# Real LLM Provider Staging Gate Report - MVP-006

## Layer
TRAINER-PLATFORM-MVP-006-DEEPSEEK-V4-FLASH-STAGING-GATE

## Date
2026-06-05

## Selected Provider
DeepSeek

## Verdict
ACCEPTED_WITH_BLOCKERS

## Summary
Railway staging backend variables for DeepSeek are present, and `OPENAI_API_KEY` remains absent. A controlled synthetic staging smoke was executed.

The smoke produced a structured evaluation and updated progress, but the evaluation result reported `ai_model_used=gpt-4o-mini` instead of `deepseek-v4-flash`. This means the deployed backend did not use the selected DeepSeek provider/model for the success case.

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
| Real DeepSeek model observed | FAIL - response reported `gpt-4o-mini` |
| Structured evaluation schema | PASS |
| Progress after evaluation | PASS |
| Analytics privacy event path | PASS |

## Blocking Diagnosis

The deployed backend appears not to map the provider-neutral MVP-006 variables (`AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, etc.) into the existing AI Gateway runtime settings. As a result, the smoke test succeeded structurally but did not prove real DeepSeek usage.

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
fix_deepseek_ai_gateway_env_mapping_then_redeploy_staging
```
