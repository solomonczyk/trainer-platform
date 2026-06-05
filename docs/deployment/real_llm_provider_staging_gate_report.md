# Real LLM Provider Staging Gate Report - MVP-006

## Layer
TRAINER-PLATFORM-MVP-006-REAL-LLM-PROVIDER-STAGING-GATE

## Date
2026-06-05

## Selected Provider
DeepSeek

## Verdict
NEEDS_OPERATOR_ACTION

## Summary
MVP-006 provider selection has changed from OpenAI to DeepSeek. OpenAI must not be configured for this gate.

Railway staging backend variable names were inspected with values redacted. The required DeepSeek secret and real-provider staging flags are not configured yet, so no real-provider enablement or smoke test was performed.

## Required Railway Staging Backend Variables

```text
DEEPSEEK_API_KEY=<secret only>
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

| Variable | Present in Railway staging backend | Notes |
|---|---:|---|
| `DEEPSEEK_API_KEY` | false | Required operator secret |
| `AI_PROVIDER` | false | Must be `deepseek` |
| `AI_REAL_PROVIDER_ENABLED` | false | Must be `true` in staging only |
| `AI_MODEL_EVALUATOR` | false | Must be `deepseek-v4-flash` |
| `AI_PROVIDER_BASE_URL` | false | Must be `https://api.deepseek.com` |
| `AI_MAX_COST_PER_REQUEST_USD` | false | Must be `0.05` |
| `AI_TIMEOUT_SECONDS` | false | Must be `30` |
| `AI_FALLBACK_PROVIDER` | false | Must be `mock` |
| `AI_EVALUATION_JSON_SCHEMA_REQUIRED` | false | Must be `true` |
| `OPENAI_API_KEY` | false | Must remain absent for this gate |

No secret values were printed, copied, committed, or stored in documentation.

## Implementation Note
DeepSeek exposes an OpenAI-compatible API surface at `https://api.deepseek.com`. Before real-provider smoke, the backend must map the provider-neutral MVP-006 variables above into the existing AI Gateway/provider adapter path without exposing secrets and without enabling OpenAI.

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
operator_configure_deepseek_staging_secret
```
