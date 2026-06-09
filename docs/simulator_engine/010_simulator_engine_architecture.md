# Layer 010 — Simulator Engine Architecture

## Overview

The immersive simulator engine replaces the form-based assessment flow with a typed, narrative-driven quest system. The engine is organized into a clear layered architecture:

```
Quest Data (JSON/Pydantic contracts)
  → Quest Service (orchestration logic)
    → Evaluator (deterministic / AI rubric)
    → Repository (DB persistence)
      → QuestSession / QuestStepResult models
```

## Key Components

### Backend (`backend/app/modules/quests/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Pydantic schemas: `QuestDefinition`, `QuestStep`, `QuestAnswerRequest/Response`, `QuestOutcomeResponse` |
| `evaluator.py` | Deterministic scoring for 7 closed types; AI rubric wrapper for free_text/dialogue |
| `quest_data.py` | QA and BA quest definitions with full content, characters, steps, outcomes |
| `repository.py` | DB operations for QuestSession and QuestStepResult |
| `service.py` | Quest lifecycle: start, submit, evaluate, advance, complete, outcome, debrief |
| `router.py` | FastAPI endpoints: `/api/v1/quests/*` |

### Frontend (`frontend/src/`)

| File | Purpose |
|------|---------|
| `features/quests/interaction-renderers.tsx` | 9 typed interaction components (SingleChoice, MultipleChoice, FreeText, Ordering, Matching, EvidenceSelect, Decision, Dialogue, branching via Decision) |
| `app/trainers/[slug]/quests/page.tsx` | Quest catalog page |
| `app/trainers/[slug]/quests/[questId]/page.tsx` | Main quest play page with full state machine |

## State Machine

```
IDLE → INTRO → READY → SUBMITTING → FEEDBACK → READY (next step)
                                      → TIMED_OUT → RETRY → EVALUATING → FEEDBACK
                                      → FAILED → RETRY → EVALUATING → FEEDBACK
                                      → OUTCOME → DEBRIEF
```

## Data Flow

1. User opens quest catalog → `GET /api/v1/quests`
2. User starts quest → `POST /api/v1/quests/{questId}/start` → creates `QuestSession` + first `QuestStepResult`
3. User answers step → `POST /api/v1/quests/sessions/{sessionId}/answer` → evaluates (deterministic or AI) → applies consequences → advances to next step
4. User completes quest → `POST /api/v1/quests/sessions/{sessionId}/complete` → selects outcome → generates debrief
5. User refreshes → `GET /api/v1/quests/sessions/{sessionId}/progress` → resumes from current step

## Persistence

- `QuestSession` table: tracks narrative state, current step, completed steps, flags, outcome, debrief
- `QuestStepResult` table: per-step answers, evaluation results, AI metadata, retry count
- Full resume support: localStorage session_id → API progress endpoint → restore exact position
