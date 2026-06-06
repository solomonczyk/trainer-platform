# Platform Capability Mapping — Trainer Platform vs BA Trainer Requirements

## Audit Date

2026-06-06

## Target System

Trainer Platform (Railway staging, `master` branch)

## Capability Matrix

| Capability | Current Support | Evidence | Migration Impact | Required Change |
|---|---|---|---|---|
| Trainer Package Schema | **supported** | `trainer_packages/qa_engineer_interview_trainer/trainer.json` defines product identity, locale, target audience. Schema is extensible. | BA pack can follow same pattern. Add BA-specific module/track field. | None — existing schema is generic enough. |
| Scenarios | **supported** | `Scenario` model with steps, skills, rubrics. Multi-step interview flow in QA pack. | BA interview questions map to scenario steps. Deterministic questions need new activity type. | Add activity_type field to scenario steps. |
| Attempts | **supported** | `Attempt` model with status tracking, retry support, evaluation linkage. | Direct mapping. Source attempts count maps to platform Attempt.retry field. | None. |
| Evaluations | **supported** | `Evaluation` + `EvaluationCriterionResult` models. DeepSeek/Mock AI gateway. | AI evaluation for open-text answers maps directly. Deterministic needs new path. | Add deterministic_evaluation_result field to Attempt or new simple_evaluations table. |
| Criteria/Rubrics | **supported** | `Rubric` + `RubricCriterion` models with weights, evidence, pass_score. | BA rubrics can follow QA pattern. Additional criteria for deterministic checks. | None — add BA-specific rubrics. |
| Authentication | **supported** | JWT auth, registration, login, profile, email/password. Full user model. | Source has no auth — all users will need platform accounts. | No platform change needed. Migration must add auth layer. |
| Progress | **supported** | `TrainerProgress` per user per trainer. Average score, completed scenarios, readiness, skill scores, last activity. | Direct mapping from source `ProgressState`. Module progress maps to platform skill scores. | Add module-level progress tracking (platform has only scenario-level). |
| Analytics | **supported** | `AnalyticsEvent` model with event_type, properties, timestamp. Auth middleware. | Source has no analytics. Add BA events to existing events table. | No platform change. Add event type constants for BA. |
| Frontend Rendering | **partial** | Next.js App Router, Tailwind UI. Supports textarea-based scenario runner. No multi-question interactive components. | BA needs 7+ interactive question types (radio, checkbox, etc.). Current frontend only renders textarea. | Build new ActivityRenderer component with pluggable question type components. |
| Localization | **supported** | ru-RU and en-US locale packs per trainer. Fallback chain. | Source is Russian-only. Add en-US translation for BA pack. | No platform change. |
| DeepSeek AI Evaluation | **supported** | `AIGatewayService` with DeepSeek provider. Timeout, fallback, cost tracking. | Open-text BA questions use DeepSeek. Keyword pre-filter can reduce costs. | No platform change needed. |
| Deterministic Validation | **missing** | No rule-based validation. Only AI evaluation exists. | Needed for radio, checkbox, number, fill-blanks, matching. | Build `DeterministicValidator` service — lightweight exact/pattern matching. |
| Exam Mode | **missing** | No timed, multi-question exam flow. Only single-scenario flow exists. | BA final exam (25 questions, 45min timer) needs new runtime flow. | Build `ExamSession` model, timer, sequential question delivery, score aggregation. |
| Diagnostics Mode | **missing** | No diagnostics assessment with level calculation. | BA diagnostics (8 questions → J/M/S) needs new flow. | Build `DiagnosticAssessment` model, level calculation, recommendations. |
| XP / Gamification | **missing** | `xp` field in source but no platform equivalent. | BA source has XP (10/5/1). Optional gamification layer. | Add optional `xp_ledger` table or use `metadata_json` on progress. |
| Question Interaction Components | **missing** | Textarea only in scenario runner. No radio, checkbox, drag, etc. | BA needs 7+ interactive component types built in the frontend. | Build shared component library: RadioGroup, CheckboxGroup, NumberInput, FillBlanks, Matching, Flashcard, KeywordTextarea. |
| Activity Types | **partial** | `Scenario` model has `steps` with text prompts only. No typed activity system. | BA needs activity_type per question (radio, checkbox, etc.). | Add `activity_type` enum to scenario steps. |
| Timer | **missing** | No countdown timer in scenario runtime. | BA exam needs 45-minute timer. | Add optional `timer_seconds` to session/attempt. |
| Data Aggregation / Reports | **partial** | Progress summary endpoint, skill scores. No exam report, no module breakdown. | BA report page shows module-by-module breakdown, weak spots. | Add module-level aggregation to progress service. |

## Summary

| Category | Count |
|---|---|
| Supported | 8 capabilities |
| Partial | 2 capabilities |
| Missing | 7 capabilities |

## Blocking Gaps for Phase 1

1. **Question interaction components** — no radio, checkbox, etc. in frontend
2. **Deterministic validation** — no rule-based answer checking backend
3. **Activity type system** — no typed activities in scenario/step model

## Blocking Gaps for Phase 2

4. **Open-text AI evaluation integration** — needs BA-specific rubrics and prompts
5. **Diagnostics mode** — needs level calculation algorithm

## Blocking Gaps for Phase 3

6. **Exam mode** — needs timer, sequential flow, score aggregation
7. **XP/gamification** — needs ledger table and frontend display
8. **Advanced interactions** — drag-sort, matching, flashcard components
