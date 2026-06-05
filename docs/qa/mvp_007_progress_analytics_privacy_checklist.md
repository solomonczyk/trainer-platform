# MVP-007 Progress, Analytics, and Privacy Checklist

## Purpose

Verify that real DeepSeek evaluations update learner progress correctly while analytics remains privacy-safe.

## Required Checklist

```json
{
  "progress_total_attempts_increments": true,
  "average_score_updates": true,
  "completed_scenarios_updates_if_passed": true,
  "analytics_event_recorded_or_skip_documented": true,
  "raw_answers_absent_from_analytics": true,
  "secrets_absent_from_logs": true
}
```

## Progress Verification

| Check | Expected result | Blocker if |
|---|---|---|
| Before evaluation progress snapshot captured | Baseline recorded for synthetic user | Baseline unavailable and cannot be reconstructed |
| total attempts increments after valid evaluation | +1 for accepted evaluation | No increment after valid evaluation |
| average score updates | New rolling average includes latest score | Average unchanged or impossible value |
| completed scenarios updates if passed | +1 when `passed=true` | Passed evaluation does not increment completed scenarios |
| failed/safe-failure evaluation | Does not create misleading progress success | Failure counted as validated success |
| repeated attempt by same user | New attempt increments without overwriting history | Prior progress lost |

## Analytics Verification

| Check | Expected result | Blocker if |
|---|---|---|
| evaluation event | Recorded or intentionally skipped with documented reason | Silent unknown behavior |
| metadata | Contains safe IDs, trainer slug, scenario key, score/model where allowed | Stores raw answer |
| raw answer | Absent from analytics event payload/storage | Present in analytics |
| provider secret | Absent from analytics and proof | Any secret value appears |
| model identifier | May store `deepseek-v4-flash` | Stores API key or auth header |

## Privacy Verification

| Area | Required result |
|---|---|
| Proof files | No raw answer text, provider keys, auth tokens, database URLs, or user secrets |
| Logs copied into docs | Sanitized excerpts only |
| Synthetic risky/private data case | Uses fake private-like values only |
| Frontend | No provider secret variables or direct provider calls |
| Production | No production data or production secrets used |

## Evidence Template

```json
{
  "case_id": "",
  "progress_before": {
    "total_attempts": null,
    "completed_scenarios": null,
    "average_score": null
  },
  "progress_after": {
    "total_attempts": null,
    "completed_scenarios": null,
    "average_score": null
  },
  "analytics_status": "TBD",
  "raw_answer_absent_from_analytics": null,
  "secrets_absent_from_logs": null,
  "decision": "TBD"
}
```

