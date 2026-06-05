# Real LLM Provider Staging Smoke Test Report - MVP-006

## Date
2026-06-05

## Selected Provider
DeepSeek

## Target Model
`deepseek-v4-flash`

## Verdict
PASSED_REAL_DEEPSEEK_STAGING_SMOKE

## Summary
A controlled synthetic staging smoke test was executed after the MVP-006C DeepSeek schema contract fix and Railway staging backend redeploy.

The smoke proved real DeepSeek usage and schema validity: the evaluation response reported `ai_model_used=deepseek-v4-flash`, returned `validation_status=validated`, produced a valid non-empty criteria array, did not expose `reasoning_content`, updated trainer progress, and accepted a privacy-safe analytics event. OpenAI remained disabled/absent for this gate.

## Smoke Test Status

| Check | Status |
|---|---|
| Synthetic user created | PASS |
| DeepSeek variables present | PASS |
| OpenAI key absent | PASS |
| DeepSeek provider/model observed | PASS - `deepseek-v4-flash` |
| Structured evaluation result | PASS |
| Evaluation schema validation | PASS - `validated` |
| Score returned | PASS - 100 |
| Passed boolean returned | PASS - true |
| Criteria returned | PASS - 1 valid criterion |
| Reasoning content exposure | PASS - not exposed |
| Latency/cost recorded | PASS - 4859 ms, USD 0.001 |
| Progress after evaluation | PASS - total_attempts 1, completed_scenarios 1, average_score 100.0 |
| Analytics event | PASS - recorded |
| Analytics privacy path | PASS - raw answer not echoed |
| Fallback/safe failure check | NOT EXECUTED - success path only per task scope |

## Smoke Evidence

```json
{
  "synthetic_user_only": true,
  "ai_model_used": "deepseek-v4-flash",
  "expected_model": "deepseek-v4-flash",
  "deepseek_model_observed": true,
  "openai_fallback_absent": true,
  "overall_score": 100,
  "passed": true,
  "validation_status": "validated",
  "criteria_schema_valid": true,
  "criteria_count": 1,
  "reasoning_content_exposed": false,
  "ai_latency_ms": 4859,
  "ai_cost_usd": 0.001,
  "strengths_count": 2,
  "weak_points_count": 0,
  "progress_total_attempts_after_evaluation": 1,
  "progress_completed_scenarios_after_evaluation": 1,
  "progress_average_score_after_evaluation": 100.0,
  "analytics_status": "recorded",
  "analytics_raw_answer_echoed": false
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
