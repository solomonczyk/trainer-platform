# Real OpenAI Staging Gate Report - MVP-006

## Layer
TRAINER-PLATFORM-MVP-006-REAL-OPENAI-STAGING-GATE

## Date
2026-06-05

## Verdict
NEEDS_OPERATOR_ACTION

## Summary
The real OpenAI staging gate was started from a clean `master` branch after MVP-005B acceptance. Preflight passed and Railway staging was reachable for variable inspection, but the required OpenAI secret is not configured in the Railway staging backend service.

Because `OPENAI_API_KEY` is unavailable, real OpenAI was not enabled and no real-provider smoke test was run.

## Preflight

| Check | Result |
|---|---|
| Branch | `master` |
| Git clean before work | true |
| Remote configured | true |
| `.env.railway.local` ignored | true |
| Secrets tracked | false |

## OpenAI Staging Secret Check

Railway backend staging variable names were inspected with values redacted. The following required variables were not present:

```text
OPENAI_API_KEY
AI_PROVIDER
AI_REAL_PROVIDER_ENABLED
AI_MODEL_EVALUATOR
AI_MAX_COST_PER_REQUEST_USD
AI_TIMEOUT_SECONDS
AI_FALLBACK_PROVIDER
AI_EVALUATION_JSON_SCHEMA_REQUIRED
```

No secret values were printed, copied, committed, or stored in documentation.

## Required Operator Action

Configure the OpenAI key as a Railway staging backend secret only, then rerun MVP-006:

```text
OPENAI_API_KEY=<secret value in Railway staging only>
AI_PROVIDER=openai
AI_REAL_PROVIDER_ENABLED=true
AI_MODEL_EVALUATOR=<validated model id>
AI_MAX_COST_PER_REQUEST_USD=0.05
AI_TIMEOUT_SECONDS=30
AI_FALLBACK_PROVIDER=mock
AI_EVALUATION_JSON_SCHEMA_REQUIRED=true
```

The application currently uses `AI_GATEWAY_*` setting names internally, so the rerun must also verify that the staging configuration maps to the deployed backend settings before smoke testing.

## Forbidden Actions Check

```json
{
  "openai_key_exposed": false,
  "openai_key_committed": false,
  "real_openai_enabled_in_staging": false,
  "real_openai_enabled_in_production": false,
  "production_deployed": false,
  "production_accepted": false,
  "release_allowed": false,
  "new_trainer_added": false,
  "payments_added": false,
  "market_launch": false
}
```

## Next Action

```text
operator_configure_openai_staging_secret
```
