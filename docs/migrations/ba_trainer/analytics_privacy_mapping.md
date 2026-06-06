# Analytics & Privacy Mapping

## Source State

The source bi-trainer-local application has **no analytics tracking**. Events are not emitted, and no user behavior is logged beyond localStorage progress.

## Target Analytics Events

All events are stored in the existing `AnalyticsEvent` model with `user_id`, `event_type`, `session_id`, `trainer_slug`, `scenario_id`, `properties`, and `event_timestamp`.

### Event Definitions

| Event Type | Trigger | Properties (public) | Properties (excluded for privacy) |
|---|---|---|---|
| `ba_trainer_opened` | User visits BA trainer detail page | `{trainer_slug, locale}` | — |
| `ba_module_opened` | User opens a module/track | `{module_id, module_title}` | — |
| `ba_activity_started` | User starts an activity | `{activity_id, activity_type, evaluation_mode}` | — |
| `ba_answer_submitted` | User submits an answer | `{activity_id, activity_type, evaluation_mode, is_retry}` | `{raw_answer, answer_text}` |
| `ba_answer_evaluated` | Evaluation completed | `{activity_id, status, score, evaluation_mode, latency_ms, cost_usd}` | `{deepseek_reasoning, raw_ai_output}` |
| `ba_hint_used` | User requests a hint | `{activity_id}` | — |
| `ba_diagnostics_started` | User starts diagnostics | `{diagnostics_version}` | — |
| `ba_diagnostics_completed` | Diagnostics finished | `{level, scores_by_tier}` | `{raw_answers}` |
| `ba_exam_started` | User starts an exam | `{question_count, duration_minutes}` | — |
| `ba_exam_completed` | Exam finished | `{score, total, time_spent, passed}` | `{answer_details}` |
| `ba_report_viewed` | User views report | `{report_type}` | `{progress_snapshot}` |

## Privacy Rules

```json
{
  "raw_answers_in_analytics": false,
  "personal_data_in_analytics": false,
  "deepseek_reasoning_in_analytics": false,
  "secrets_in_analytics": false
}
```

### Detailed Rules

1. **Raw answers are never logged to analytics.** The `properties` field of `AnalyticsEvent` must not contain `answer_text`, `answer_json`, or any user-submitted content.
2. **Personal data is never logged.** No email, name, IP address beyond request metadata, or any PII.
3. **DeepSeek reasoning output is never logged.** The `raw_ai_output` field from `Evaluation` is stored in the `evaluations` table only, not in analytics.
4. **No secrets or credentials.** Analytics events must never contain tokens, passwords, or API keys.

### Analytics Event Example (Allowed)

```json
{
  "event_type": "ba_answer_evaluated",
  "properties": {
    "activity_id": "ba_hr_q1_radio",
    "activity_type": "single_choice",
    "evaluation_mode": "deterministic",
    "status": "correct",
    "score": 100,
    "latency_ms": 2
  }
}
```

### Analytics Event Example (Forbidden — would be rejected)

```json
{
  "event_type": "ba_answer_submitted",
  "properties": {
    "activity_id": "ba_hr_q1_radio",
    "answer_text": "This is my answer to the question...",  // FORBIDDEN
    "personal_email": "user@example.com"                    // FORBIDDEN
  }
}
```

## Server-Side Privacy Enforcement

The analytics service must strip any keys matching the pattern:
- `answer*`
- `raw_*`
- `email*`
- `password*`
- `token*`
- `secret*`

Before persisting `AnalyticsEvent.properties`.

## Data Retention

| Data Type | Retention | Notes |
|---|---|---|
| Analytics events | 90 days | Rolling window, auto-purge |
| Evaluation AI reasoning | 30 days | Stored in `Evaluation.raw_ai_output` |
| User answers | Duration of account | Needed for progress and reports |
| Personal data | Duration of account | Per platform privacy policy |
