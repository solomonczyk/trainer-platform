# Gap Analysis & Priorities

## Classification

Each gap is classified as:

- **already_supported** — Platform already provides this capability
- **reusable_shared_capability** — Can be built once and shared across all trainers
- **BA_specific_feature** — Only needed for the BA trainer
- **platform_wide_schema_extension** — Requires schema change affecting all trainers
- **migration_blocker** — Must be resolved before any BA content can be migrated
- **optional_polish** — Nice-to-have, not blocking

## Gap Inventory

| Gap | Category | Priority | Platform Component | Effort |
|---|---|---|---|---|
| **Activity type system** — No typed activity discriminator | migration_blocker | P0 | Backend schema + frontend renderer | Medium |
| **Question interaction components** — No radio, checkbox, etc. | migration_blocker | P0 | Frontend shared component library | Large |
| **Deterministic validator** — No rule-based answer checking | migration_blocker | P0 | Backend service | Small |
| **Content import format** — No standard for deterministic questions | migration_blocker | P0 | Package schema + converter | Medium |
| **AI evaluation for open-text** — Already exists for scenarios | already_supported | — | Backend AI Gateway | Already done |
| **Progress per user per trainer** — Already exists | already_supported | — | Backend progress module | Already done |
| **Analytics events** — Already exists | already_supported | — | Backend analytics module | Already done |
| **Localization** — Locale packs already supported | already_supported | — | Package schema | Already done |
| **Auth and user isolation** — Already exists | already_supported | — | Auth module | Already done |
| **Enrollment flow** — Already exists | already_supported | — | Platform flow | Already done |
| **BA-specific skill map** — BA domain skills | BA_specific_feature | P0 | Content in skill_map.json | Small |
| **BA-specific rubrics** — Evaluation criteria for BA | BA_specific_feature | P0 | Content in rubric_pack.json | Small |
| **BA scenarios and activities** — Core content | BA_specific_feature | P0 | Content in scenarios/ | Medium |
| **BA locale (ru-RU)** — Russian-language strings | BA_specific_feature | P0 | Content in locales/ru-RU.json | Small |
| **Diagnostics mode** — Level assessment flow | BA_specific_feature | P1 | Backend + frontend diagnostic flow | Medium |
| **Exam mode** — Timed multi-question exam | BA_specific_feature | P1 | Backend + frontend exam flow | Large |
| **Module/track grouping** — Organize activities into modules | platform_wide_schema_extension | P1 | Track model already exists; add module hierarchy | Small |
| **Hybrid evaluation** — Keyword pre-check + AI | reusable_shared_capability | P1 | Orchestration service | Medium |
| **Keyword-based text evaluation** — Deterministic text check | reusable_shared_capability | P0 | Shared validator utility | Small |
| **Timer capability** — Countdown for exam mode | reusable_shared_capability | P1 | Frontend hook + optional backend tracking | Small |
| **Report/aggregation** — Module-level progress breakdown | reusable_shared_capability | P1 | Progress service extension | Medium |
| **Drag-sort component** — Drag-and-drop ordering | reusable_shared_capability | P2 | Frontend component | Medium |
| **Matching component** — Column matching | reusable_shared_capability | P2 | Frontend component | Medium |
| **Flashcard component** — Self-assessed cards | reusable_shared_capability | P2 | Frontend component | Small |
| **Interactive board, click-image, branching dialogue, etc.** | optional_polish | P2 | Frontend components | Large |
| **XP / gamification ledger** | optional_polish | P2 | Backend table + frontend display | Medium |
| **Audio recording** | optional_polish | P2 | Frontend component (MediaRecorder) | Small |
| **English localization (en-US)** | optional_polish | P2 | Translation content | Medium |

## Priority Summary

| Priority | Label | Count | Key Items |
|---|---|---|---|
| P0 | Required for first native BA pack | 8 | Activity types, question components, deterministic validator, content format, BA skill map, rubrics, scenarios, locales |
| P1 | Required for full source feature parity | 6 | Diagnostics, exam, module hierarchy, hybrid evaluation, timer, reporting |
| P2 | Optional polish | 7 | Advanced interactions, XP, audio, en-US locale |

## Migration Blockers

The following gaps must be resolved before any BA content can be migrated:

1. **Activity type system** — Without a way to distinguish `single_choice` from `free_text` from `exam`, the platform cannot route questions to the correct renderer or validator.
2. **Question interaction components** — Without radio buttons, checkboxes, number inputs, fill-in-blanks, and matching components in the frontend, users cannot interact with deterministic questions.
3. **Deterministic validator** — Without rule-based answer checking, correct/incorrect determination cannot happen server-side.
4. **Content import format** — Without a standard way to represent deterministic questions in the trainer package JSON, content cannot be imported.
