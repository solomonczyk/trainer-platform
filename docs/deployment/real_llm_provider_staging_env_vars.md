# Real LLM Provider Staging Environment Variables - MVP-006

## Status
NEEDS_OPERATOR_ACTION

## Selected Provider
DeepSeek

## Scope
These variables are for the Railway staging backend service only. They must not be configured in frontend services or production during MVP-006.

## Required Staging Backend Variables

| Variable | Required value | Status |
|---|---|---|
| `DEEPSEEK_API_KEY` | Secret value stored only in Railway staging backend | Missing |
| `AI_PROVIDER` | `deepseek` | Missing |
| `AI_REAL_PROVIDER_ENABLED` | `true` | Missing |
| `AI_MODEL_EVALUATOR` | `deepseek-v4-flash` | Missing |
| `AI_PROVIDER_BASE_URL` | `https://api.deepseek.com` | Missing |
| `AI_MAX_COST_PER_REQUEST_USD` | `0.05` | Missing |
| `AI_TIMEOUT_SECONDS` | `30` | Missing |
| `AI_FALLBACK_PROVIDER` | `mock` | Missing |
| `AI_EVALUATION_JSON_SCHEMA_REQUIRED` | `true` | Missing |

## Explicitly Forbidden

```text
OPENAI_API_KEY
```

OpenAI must not be configured or enabled for this gate.

## Backend Compatibility Check Required On Rerun

The backend currently uses the AI Gateway and provider adapter path for real LLM calls. On rerun, verify that the deployed backend reads the provider-neutral variables above or has a safe compatibility mapping before smoke testing DeepSeek.

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
