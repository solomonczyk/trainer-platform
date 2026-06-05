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
A controlled synthetic staging smoke test was executed after the backend AI Gateway environment mapping fix and Railway staging backend redeploy.

The smoke proved real DeepSeek usage: the evaluation response reported `ai_model_used=deepseek-v4-flash`, returned `validation_status=validated`, produced a structured score, updated trainer progress, and accepted a privacy-safe analytics event. OpenAI remained disabled/absent for this gate.

## Smoke Test Status

| Check | Status |
|---|---|
| Synthetic user created | PASS |
| DeepSeek variables present | PASS |
| OpenAI key absent | PASS |
| DeepSeek provider/model observed | PASS - `deepseek-v4-flash` |
| Structured evaluation result | PASS |
| Evaluation schema validation | PASS - `validated` |
| Score returned | PASS - 88 |
| Passed boolean returned | PASS - true |
| Criteria returned | PASS - 3 criteria |
| Progress after evaluation | PASS - total_attempts 1, completed_scenarios 1, average_score 88.0 |
| Analytics event | PASS - recorded |
| Analytics privacy path | PASS - privacy-safe metadata only |
| Fallback/safe failure check | NOT EXECUTED - success path only per task scope |

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
  "strengths_count": 5,
  "weak_points_count": 5,
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
