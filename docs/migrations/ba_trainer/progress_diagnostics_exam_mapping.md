# Progress, Diagnostics & Exam Mapping

## Source State Shape

```typescript
interface ProgressState {
  answers: Record<string, AnswerRecord>;
  diagnosticsResult: DiagnosticsResult | null;
  examResult: ExamResult | null;
  xp: number;
  lastActive: number;
}
```

## Target Mapping

### Answers → Attempts

| Source | Target | Notes |
|---|---|---|
| `answers[questionId]` | `Attempt` per activity | One attempt per question attempt |
| `.status: 'correct' | 'incorrect' | 'partial' | 'pending'` | `Attempt.status` + `Evaluation.score` | `correct` maps to evaluation score ≥90, `partial` to 50-89, `incorrect` to <50 |
| `.answer` | `Attempt.answer_text` + `Attempt.answer_json` | Structure depends on activity type |
| `.attempts` | `Attempt.is_retry` + `Attempt.retry_of_attempt_id` | Incrementing counter in source maps to retry chain in platform |
| `.answeredAt` | `Attempt.completed_at` | Timestamp |

**Design Decisions:**

- **No browser-only source of truth.** All answers must be persisted server-side.
- **User isolation.** Every attempt is tied to a `user_id`.
- **Cross-device progress.** Server-side progress enables login from any device.
- **Idempotent updates.** Submitting the same answer twice does not create duplicate attempts.
- **Retries recorded separately.** Each retry is a new `Attempt` record linked via `retry_of_attempt_id`.
- **Exam attempts immutable.** Once an exam attempt is completed, it cannot be modified.

### Answer Status → Activity Result Status

| Source Status | Platform Equivalent | Criteria |
|---|---|---|
| `correct` | `passed` | Deterministic: exact match. AI: score ≥70. |
| `partial` | `partial` | Deterministic: partial match (m out of n). AI: score 30-69. |
| `incorrect` | `failed` | Deterministic: no match. AI: score <30. |
| `pending` | `in_progress` | Not yet evaluated. |

### Diagnostics Result → Diagnostic Assessment

| Source | Target | Notes |
|---|---|---|
| `diagnosticsResult.level` (`J` / `M` / `S`) | `SkillScore.level` for diagnostic skills | Stored per-skill for each user |
| `diagnosticsResult.scores` | Multiple `SkillScore` records | Per-category scores from source |
| `diagnosticsResult.completedAt` | `TrainerProgress.updated_at` | Timestamp |

**Level Calculation (source algorithm, to be adapted):**

```typescript
function determineLevel(answers): Level {
  // Score per level tier
  const seniorPct = seniorCorrect / seniorTotal;  // ≥0.6 → Senior
  const middlePct = middleCorrect / middleTotal;  // ≥0.6 → Middle
  return seniorPct >= 0.6 ? 'S' : middlePct >= 0.6 ? 'M' : 'J';
}
```

**Platform adaptation:**

- Store per-question result as `Attempt` records
- Calculate level on-the-fly from skill scores
- Cache level in `TrainerProgress.metadata_json.diagnostic_level`
- Recalculate on diagnostic rerun

### Exam Result → Exam Session & Summary

| Source | Target | Notes |
|---|---|---|
| `examResult.score` | `ExamSession.score` | Correct count |
| `examResult.total` | `ExamSession.total_questions` | Question count |
| `examResult.answers` | Array of `Attempt` records | One per exam question |
| `examResult.completedAt` | `ExamSession.completed_at` | Timestamp |
| `examResult.timeSpent` | `ExamSession.time_spent_seconds` | Duration |

**Exam Session Model (proposed):**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "trainer_product_id": "uuid",
  "status": "in_progress|completed|timed_out",
  "started_at": "timestamp",
  "completed_at": "timestamp|null",
  "time_spent_seconds": 2700,
  "total_questions": 25,
  "score": 18,
  "passed": true,
  "attempt_ids": ["uuid1", "uuid2", ...]
}
```

**Exam Rules:**

- Questions are randomly selected from the full question pool
- Each exam session creates independent `Attempt` records
- On completion (or timeout), all unanswered questions are marked `failed`
- Exam can be retried; each retry is a new `ExamSession`
- Previous exam sessions are read-only

### XP → Optional Gamification Ledger

| Source | Target | Notes |
|---|---|---|
| `xp` (aggregate) | `XPLedger.total_xp` or `TrainerProgress.metadata_json.xp` | Optional |
| XP per answer: correct=10, partial=5, incorrect=1 | `XPLedgerTransaction` | Each answer event adds a transaction |

**Design Decision:** XP is **optional** in the platform. The source XP system is simple and can be stored in `TrainerProgress.metadata_json.xp` without a dedicated table. A full ledger can be added later (P2).

### Last Activity → Trainer Progress

| Source | Target |
|---|---|
| `lastActive: Date.now()` | `TrainerProgress.last_activity_at` |

Updated on every answer submission, diagnostics completion, exam action.

---

## Progress Persistence Rules

| Rule | Implementation |
|---|---|
| No browser-only source of truth | All writes go to API |
| User isolation | `user_id` on all tables |
| Cross-device progress | Server-side storage, JWT auth |
| Idempotent updates | Upsert by `(user_id, activity_id, session_id)` |
| Retries recorded separately | New `Attempt` with `is_retry=true` |
| Exam attempts immutable | `status: 'completed'` + no-update constraint |
| Diagnostics versioned | `metadata_json.diagnostics_version` for schema evolution |

## Attempt Immutability

Once an attempt is evaluated:

- `status` is set to `completed` or `evaluated`
- `score`, `answer_text`, and `evaluation_id` become immutable
- No PUT/PATCH endpoint for evaluated attempts
- Exam attempts additionally lock `exam_session_id`
- Retries create new attempts; original is preserved as reference
