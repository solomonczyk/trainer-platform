# Real LLM Provider Staging Environment Variables - MVP-006

## Status
CONFIGURED_IN_RAILWAY_STAGING_BACKEND

## Selected Provider
DeepSeek

## Scope
These variables are for the Railway staging backend service only. They must not be configured in frontend services or production during MVP-006.

## Required Staging Backend Variables

Values were not printed or stored.

| Variable | Required value | Presence |
|---|---|---|
| `DEEPSEEK_API_KEY` | Secret value stored only in Railway staging backend | Present |
| `AI_PROVIDER` | `deepseek` | Present |
| `AI_REAL_PROVIDER_ENABLED` | `true` | Present |
| `AI_MODEL_EVALUATOR` | `deepseek-v4-flash` | Present |
| `AI_PROVIDER_BASE_URL` | `https://api.deepseek.com` | Present |
| `AI_MAX_COST_PER_REQUEST_USD` | `0.05` | Present |
| `AI_TIMEOUT_SECONDS` | `30` | Present |
| `AI_FALLBACK_PROVIDER` | `mock` | Present |
| `AI_EVALUATION_JSON_SCHEMA_REQUIRED` | `true` | Present |

## Explicitly Forbidden

```text
OPENAI_API_KEY
```

Railway staging backend variable inspection showed `OPENAI_API_KEY` absent.

## Backend Compatibility Result

The backend AI Gateway compatibility mapping is now active in Railway staging. The controlled smoke result reported `ai_model_used=deepseek-v4-flash`, with `validation_status=validated`, confirming that `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, `AI_TIMEOUT_SECONDS`, and `DEEPSEEK_API_KEY` are driving the deployed evaluator path.

No provider secret value should ever be printed in terminal output, docs, proof JSON, screenshots, logs, or final reports.

## Production State

```json
{
  "real_llm_provider_enabled_in_production": false,
  "openai_enabled": false,
  "production_accepted": false,
  "release_allowed": false
}
```
