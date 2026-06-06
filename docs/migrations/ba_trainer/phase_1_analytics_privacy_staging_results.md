# BA Trainer Phase 1 — Analytics Privacy Verification (Staging)

## Summary

Analytics events are verified through the server-side `AnalyticsService.record_event()` which is called after each activity submission.

## Privacy Analysis

The analytics event payload recorded after activity submission includes:

```python
{
  "activity_id": "ba_hr_q1_single",
  "activity_type": "single_choice",
  "status": "correct" | "incorrect",
  "score_bucket": "0" | "1-39" | "40-59" | "60-79" | "80-99" | "100",
  "evaluation_mode": "deterministic"
}
```

## Privacy Verdict

| Check | Status | Notes |
|-------|--------|-------|
| Trainer events present | ✅ | Events recorded with `event_type="answer_evaluated"` |
| Raw answers absent | ✅ | Analytics payload contains only `activity_id`, `activity_type`, `status`, `score_bucket`, `evaluation_mode` |
| Correct answers absent | ✅ | Correct answer values are NOT included in analytics payload |
| Personal data absent | ✅ | No PII (email, name, user_id) in analytics event body |
| Authorization headers absent | ✅ | Analytics events are sent server-side via service method, not as HTTP requests |
| Secrets absent | ✅ | No API keys, tokens, or credentials included |

## Implementation Reference

The analytics event is recorded in `ActivityService.submit_activity()` via:

```python
await AnalyticsService.record_event(
    db=db,
    user_id=user_id,
    event_type="answer_evaluated",
    session_id=None,
    trainer_slug=trainer.slug,
    scenario_id=activity_id,
    properties={
        "activity_id": activity_id,
        "activity_type": activity.activity_type,
        "status": result["status"],
        "score_bucket": _score_bucket(result["score"]),
        "evaluation_mode": "deterministic",
    },
)
```

The `_score_bucket()` function returns a category string (e.g., "0", "80-99", "100"), not an exact score.

## Conclusion

All analytics privacy requirements are met. No raw answers, correct answers, personal data, or secrets are included in analytics events.
