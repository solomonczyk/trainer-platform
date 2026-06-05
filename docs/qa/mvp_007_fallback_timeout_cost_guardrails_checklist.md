# MVP-007 Fallback, Timeout, Rate Limit, and Cost Guardrails Checklist

## Purpose

Define the guardrail checks required before accepting staging real AI. This document is a planning checklist only and does not change Railway variables or execute provider calls.

## Required Guardrails

```json
{
  "max_cost_per_request_usd": 0.05,
  "timeout_seconds": 30,
  "rate_limit_enabled": true,
  "blind_retry_disabled": true,
  "fallback_or_safe_failure_verified": true,
  "no_unbounded_retry_loop": true
}
```

## Checklist

| Check | Expected result | Evidence required | Blocker if |
|---|---|---|---|
| Cost cap | `AI_MAX_COST_PER_REQUEST_USD=0.05` in staging backend config | Redacted variable presence/value class, no secrets | No cap or cap above approved amount |
| Timeout | `AI_TIMEOUT_SECONDS=30` | Redacted config evidence and timeout-path test | Requests hang beyond bounded timeout |
| Rate limit | Enabled for evaluation endpoints or gateway path | Rate-limit test result or config evidence | No rate limiting before broader beta |
| Blind retry disabled | Retries are bounded and observable | Code/config evidence, failure-path result | Unbounded retry loop |
| Fallback/safe failure | Provider failure returns explicit fallback or safe failure | Failure test response and proof status | Fallback reported as real DeepSeek success |
| Cost telemetry | Per-request cost estimate recorded when available | Evaluation response/admin evidence without secrets | Cost impossible to audit |
| Provider identity | Success case records DeepSeek model | `ai_model_used=deepseek-v4-flash` | Model absent or OpenAI model reported |
| Secret handling | No key in docs, logs, frontend, proof | Secret scan summary | Secret exposed |

## Failure-Path Expectations

| Path | Expected behavior |
|---|---|
| DeepSeek timeout | Request fails safely or returns explicit fallback status; no progress success unless product policy accepts fallback |
| DeepSeek HTTP failure | Safe error/fallback; no fake `validated` success |
| Malformed JSON | Normalize if possible; otherwise safe failure |
| Rate limit exceeded | Bounded response with no provider retry storm |
| Cost cap exceeded | Request blocked or marked failed safely |

## Acceptance Rule

MVP-007 cannot accept staging real AI until success-path quality and failure-path safety are both proven. Success-path DeepSeek usage alone is not enough for broader beta readiness.

