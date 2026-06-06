# Migration Execution Plan — BA Interview Trainer → Trainer Platform

## Strategy

```
Source → Content reference + interaction reference → Native trainer package + shared platform capabilities
```

No direct merge. No copied frontend. The source is a reference for content extraction and interaction design. The target is a native trainer package conforming to the platform's package schema.

## Phases

### Phase 1 — Foundation & Deterministic Content (Estimated: 3-5 sprints)

**Goal:** Migrate all deterministic question types with basic module navigation and shared progress.

#### Implementation Tasks

| Task | Description | Components | Dependencies |
|---|---|---|---|
| **1.1 Activity type system** | Add `activity_type` discriminator to platform schema. New `Activity` model or extend `ScenarioStep` with type field. | Backend schema, migration | None |
| **1.2 Deterministic validator** | Build `DeterministicValidator` service — stateless function supporting `single_choice`, `multiple_choice`, `numeric`, `fill_blanks`, `matching` validations. | Backend service | 1.1 |
| **1.3 Frontend activity components** | Build shared component library: RadioGroup, CheckboxGroup, NumberInput, FillBlanks, Matching, Flashcard, KeywordTextarea. Each with configurable data props and answer callback. | Frontend components | 1.1 |
| **1.4 Activity renderer** | Build `ActivityRenderer` component that selects the correct UI + validator based on `activity_type` and `evaluation_mode`. | Frontend renderer | 1.2, 1.3 |
| **1.5 BA pack content creation** | Create BA trainer package directory with manifest, skill map, rubrics. | Content files | — |
| **1.6 BA module import (radio/checkbox/number)** | Import 146 questions (radio 98 + checkbox 44 + number 4) as deterministic activities. | Content files + converter | 1.4, 1.5 |
| **1.7 BA module import (fill-blanks/matching)** | Import 18 questions (fill-blanks 13 + matching 5) as deterministic activities. | Content files | 1.4, 1.5 |
| **1.8 Module navigation UI** | Frontend page listing tracks/modules with progress indicators. | Frontend page | 1.6, 1.7 |
| **1.9 Shared progress integration** | Wire activities to `Attempt` + `TrainerProgress` models for persistent cross-device progress. | Backend + frontend integration | 1.6, 1.7 |

**Deliverable:** User can browse BA modules, answer radio/checkbox/number/fill-blanks/matching questions, get deterministic feedback, and see progress persist across sessions.

**Excludes:** AI evaluation, diagnostics, exam, open-text questions, XP.

---

### Phase 2 — AI Evaluation & Diagnostics (Estimated: 2-3 sprints)

**Goal:** Enable DeepSeek evaluation for open-text answers, implement diagnostics flow, add reporting.

#### Implementation Tasks

| Task | Description | Components | Dependencies |
|---|---|---|---|
| **2.1 BA-specific AI rubrics** | Create rubric definitions for textarea/case-study answers with BA-specific criteria. | Content files | Phase 1 |
| **2.2 BA AI evaluation prompts** | Create DeepSeek prompt templates for BA interview evaluation in Russian. | Prompt templates + locale | 2.1 |
| **2.3 Keyword pre-check for hybrid mode** | Add keyword matching as a pre-AI filter. If keywords satisfied → proceed to AI; else return deterministic partial result. | Backend service | 1.2 |
| **2.4 Import textarea questions (44)** | Convert 44 textarea questions as hybrid (keyword + AI) or pure AI activities. | Content files + converter | 2.3 |
| **2.5 Diagnostics architecture** | Build `DiagnosticAssessment` model + service: fixed question list, level calculation, recommendations. | Backend + frontend | 1.4 |
| **2.6 Diagnostics content** | Import 8 diagnostics questions as a diagnostic assessment activity. | Content files | 2.5 |
| **2.7 Progress reporting** | Build report page: module-by-module breakdown, weak spots identification, skill scores. | Frontend page + backend aggregation | 1.9 |
| **2.8 Analytics events** | Wire analytics events for all BA trainer interactions per spec. | Frontend + backend events | 2.7 |

**Deliverable:** User can answer open-text questions with AI evaluation, take diagnostics to determine level, view comprehensive progress report, and all events are tracked.

**Excludes:** Exam mode, advanced interactions (drag, board, etc.), XP.

---

### Phase 3 — Exam, Advanced Interactions & Full Parity (Estimated: 3-4 sprints)

**Goal:** Implement exam mode, remaining interaction types, XP, and reach full source feature parity.

#### Implementation Tasks

| Task | Description | Components | Dependencies |
|---|---|---|---|
| **3.1 Exam session model** | Build `ExamSession` model, timer service, random question selection, sequential delivery, score aggregation. | Backend + frontend | Phase 2 |
| **3.2 Exam timer UI** | Countdown timer component with visual urgency states. | Frontend component | 3.1 |
| **3.3 Exam scoring & pass/fail** | Define pass threshold (70%), attempt immutability, retry policy. | Backend | 3.1 |
| **3.4 Import exam configuration** | Define exam question pool, duration (45 min), question count (25). | Content files | 3.3 |
| **3.5 XP/gamification ledger** | Build optional XP table, transaction log, frontend display. | Backend + frontend | Phase 2 |
| **3.6 Advanced interaction components** | Build DragSort, InteractiveBoard, ClickOnImage, BranchingDialogue, TableInput, Likert components. | Frontend components | 1.4 |
| **3.7 Flashcard content (3 questions)** | Import 3 flashcard questions. | Content files | 3.6 |
| **3.8 Source quality improvements** | Compress assets, expand module 10, review keyword thresholds. | Content | Phase 2 |
| **3.9 End-to-end testing** | Full regression: all question types, diagnostics, exam, progress, analytics. | QA | 3.8 |

**Deliverable:** Full source feature parity. User can take timed exam, earn XP, use all interaction types. All 211 questions accessible.

**Excludes:** English localization, audio recording (no questions use it), unused type components with no content.

---

## Phase Summary

| Phase | Sprints | Questions Imported | New Platform Capabilities |
|---|---|---|---|
| Phase 1 | 3-5 | 164 (146 + 18) | Activity types, deterministic validator, 5 frontend components |
| Phase 2 | 2-3 | 52 (44 textarea + 8 diagnostics) | AI evaluation, hybrid mode, diagnostics, reporting, analytics |
| Phase 3 | 3-4 | 3 (flashcards) + all configured | Exam mode, XP, 6 advanced components |
| **Total** | **8-12** | **219** | **17 new capabilities** |

## Reuse Percentages

| Metric | Value |
|---|---|
| Estimated reuse % (content) | 96% (211 of 219 questions ready for direct import) |
| Estimated transform % (content) | 4% (8 diagnostics questions + dynamic exam config) |
| Estimated platform reuse % (capabilities) | 47% (8 of 17 capabilities already supported) |
| Estimated new platform code % | 53% (9 of 17 capabilities need building) |
| QA trainer unchanged | ✅ All extensions are additive |
| Source repo unchanged | ✅ Read-only reference, no modifications |
