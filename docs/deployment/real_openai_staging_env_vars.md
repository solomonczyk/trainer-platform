# Real OpenAI Staging Environment Variables - MVP-006

## Status
NEEDS_OPERATOR_ACTION

## Scope
These variables are for Railway staging backend only. They must not be configured for production during MVP-006.

## Required Staging Variables

| Variable | Required value | Status |
|---|---|---|
| `OPENAI_API_KEY` | Secret value stored only in Railway staging | Missing |
| `AI_PROVIDER` | `openai` | Missing |
| `AI_REAL_PROVIDER_ENABLED` | `true` | Missing |
| `AI_MODEL_EVALUATOR` | Validated OpenAI model id | Missing |
| `AI_MAX_COST_PER_REQUEST_USD` | `0.05` | Missing |
| `AI_TIMEOUT_SECONDS` | `30` | Missing |
| `AI_FALLBACK_PROVIDER` | `mock` | Missing |
| `AI_EVALUATION_JSON_SCHEMA_REQUIRED` | `true` | Missing |

## Internal Compatibility Check Required On Rerun

The backend currently reads AI settings through the existing AI Gateway configuration fields. Before enabling the real provider, the rerun must verify or configure compatible internal setting names:

```text
AI_GATEWAY_PROVIDER=openai
AI_GATEWAY_MODEL=<same validated model id>
AI_GATEWAY_TIMEOUT_SECONDS=30
FF_AI_EVALUATION_REAL_PROVIDER_ENABLED=true
```

No secret value should ever be printed in terminal output, docs, proof JSON, screenshots, or final reports.

## Production State

```json
{
  "production_openai_enabled": false,
  "production_accepted": false,
  "release_allowed": false
}
```
