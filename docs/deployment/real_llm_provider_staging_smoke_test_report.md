# Real LLM Provider Staging Smoke Test Report - MVP-006

## Date
2026-06-05

## Selected Provider
DeepSeek

## Target Model
`deepseek-v4-flash`

## Verdict
FAILED_REAL_PROVIDER_ASSERTION

## Summary
A controlled synthetic staging smoke test was executed after the operator configured DeepSeek variables and redeployed the backend. The user journey, structured evaluation, progress update, and analytics event path passed.

However, the evaluation response reported `ai_model_used=gpt-4o-mini`, not `deepseek-v4-flash`. Therefore this was not accepted as a real DeepSeek smoke.

## Smoke Test Status

| Check | Status |
|---|---|
| Synthetic user created | PASS |
| DeepSeek variables present | PASS |
| OpenAI key absent | PASS |
| DeepSeek provider/model observed | FAIL |
| Structured evaluation result | PASS |
| Evaluation schema validation | PASS |
| Score returned | PASS - 94 |
| Passed boolean returned | PASS - true |
| Feedback returned | PASS |
| Progress after evaluation | PASS - total_attempts 1, completed_scenarios 1, average_score 94.0 |
| Analytics event | PASS - recorded |
| Raw-answer analytics privacy path | PASS - recorded through sanitizer path |
| Fallback/safe failure check | NOT EXECUTED - blocked until real provider mapping works |

## Smoke Evidence

```json
{
  "synthetic_user_only": true,
  "ai_model_used": "gpt-4o-mini",
  "expected_model": "deepseek-v4-flash",
  "deepseek_model_observed": false,
  "score": 94,
  "passed": true,
  "validation_status": "validated",
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 1,
  "progress_average_score_after_evaluation": 94.0,
  "analytics_status": "recorded",
  "analytics_privacy_status": "recorded"
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
