# Phase 1 Progress Persistence Report

## Source of Truth

Progress is stored in PostgreSQL via the following models:
- **Attempt**: Each activity submission creates an Attempt record with status, score, answer metadata
- **DeterministicEvaluation**: Linked to Attempt, stores validation result (status, score, passed, feedback)
- **TrainerProgress**: Per-user per-trainer aggregate (average_score, completed_scenarios, total_attempts)

## Persistence Properties

| Property | Status | Implementation |
|---|---|---|
| Database source of truth | ✅ | PostgreSQL via SQLAlchemy async ORM |
| Attempts persisted | ✅ | Each submission = 1 Attempt + 1 DeterministicEvaluation |
| Retries as separate attempts | ✅ | `is_retry=True` + `retry_of_attempt_id` linking |
| Idempotency | ✅ | `idempotency_key` column, duplicate returns same result |
| User isolation | ✅ | All queries filtered by `user_id` |
| Progress recalculation | ✅ | Transactional update on every submission |
| Refresh persistence | ✅ | Data queried from DB, survives page refresh |
| Cross-device persistence | ✅ | DB-backed, visible from any authenticated session |
| Logout/login persistence | ✅ | User-scoped, survives auth token refresh |

## Progress Metrics

After each submission:
- `total_attempts` incremented by 1
- `completed_scenarios` incremented by 1 on pass
- `average_score` = rolling average of all attempt scores
- `readiness_status` = derived from score + completion count
