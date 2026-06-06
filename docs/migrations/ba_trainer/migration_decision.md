# Migration Decision — Business Analyst Interview Trainer

## Decision

**READY_FOR_IMPLEMENTATION**

## Summary

The migration of `bi-trainer-local` into the Trainer Platform as a native `business_analyst_interview_trainer` package is **feasible and recommended**. The source content is well-structured, the platform has a solid foundation, and the gaps are well-understood and addressable.

## Feasibility Assessment

```json
{
  "migration_feasible": true,
  "estimated_reuse_percent": 96,
  "estimated_transform_percent": 4,
  "blocking_gaps": [
    "activity_type_system",
    "question_interaction_components",
    "deterministic_validator",
    "content_import_format"
  ],
  "non_blocking_gaps": [
    "diagnostics_mode",
    "exam_mode",
    "hybrid_evaluation",
    "keyword_based_text_evaluation",
    "timer_capability",
    "report_aggregation",
    "drag_sort_component",
    "matching_component",
    "flashcard_component"
  ],
  "recommended_first_implementation_layer": "Phase 1 — Foundation & Deterministic Content"
}
```

## Decision Rationale

### Why Direct App Merge is Rejected

1. **Architecture mismatch** — Standalone React/Vite SPA with localStorage persistence cannot be merged into Next.js monorepo with PostgreSQL backend.
2. **Auth mismatch** — Source has no auth; platform has JWT auth. Direct merge would bypass all security.
3. **State mismatch** — Source uses client-only Zustand + localStorage; platform uses server-side PostgreSQL.
4. **Interaction model mismatch** — Source uses flat question list with client-side validation; platform uses scenario-based flows with AI evaluation.
5. **Maintenance burden** — A merged hybrid would be harder to maintain than a clean native package.

### Why Native Trainer Pack is Correct

1. **Pluggable architecture** — The existing QA trainer demonstrates the package pattern. BA follows the same contract.
2. **Shared capabilities** — Progress, auth, analytics, AI evaluation, locale — all shared across trainers.
3. **Independent versioning** — BA content can evolve independently from platform releases.
4. **Clear separation** — BA-specific components (activity types, validators) are new shared modules, not BA-specific forks.

### Blocking Gaps are Known and Addressable

The 4 blocking gaps are all infrastructure work that benefits the entire platform:
- Activity type system enables any future trainer with deterministic questions
- Question interaction components are reusable across all trainers
- Deterministic validator is a shared service
- Content import format establishes a standard for all future content packs

### Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Activity type schema extension may conflict with existing scenarios | Low | All extensions are additive (nullable fields, separate tables) |
| Frontend component development scope larger than estimated | Medium | Prioritize P0 types (radio, checkbox, number) first; P2 types later |
| AI evaluation costs for open-text questions | Low | Hybrid mode with keyword pre-check reduces unnecessary AI calls |
| Content is Russian-only | Low | en-US locale can be added in Phase 3 or later |
| QA trainer regressions from shared changes | Low | All BA changes are additive; existing QA code paths unchanged |

## Verification Steps Required Before Phase 1 Implementation

1. ✅ Source repository audit complete — 211 questions, 10 modules, 7 types
2. ✅ Deployed product review complete — routes, interactions, persistence verified
3. ✅ Platform capability mapping complete — 8 supported, 2 partial, 7 missing
4. ✅ Question type inventory complete — 7 types with questions, 9 type components without data
5. ✅ Evaluation policy defined — deterministic, AI, hybrid policies documented
6. ✅ Content mapping complete — 12 modules mapped to target structure
7. ✅ Schema proposal complete — 17 activity types, 3 evaluation modes defined
8. ✅ Migration execution plan ready — 3 phases, 8-12 sprints estimated
9. ✅ Source repository unchanged — read-only audit, no modifications
10. ✅ QA trainer unchanged — all extensions are additive

## Authorization

```json
{
  "authorized_next_action": "implement_ba_trainer_phase_1_native_vertical_slice",
  "authorized_scope": [
    "Create Activity model with type discriminator (schema migration)",
    "Build DeterministicValidator service",
    "Build frontend activity components (radio, checkbox, number, fill-blanks, matching)",
    "Build ActivityRenderer component",
    "Create BA trainer package structure",
    "Import 164 deterministic questions as activities",
    "Build module navigation UI",
    "Wire progress persistence"
  ],
  "not_authorized": [
    "Modify existing QA trainer scenarios or runtime",
    "Enable OpenAI provider",
    "Deploy to production",
    "Set production_accepted=true",
    "Set release_allowed=true",
    "Add payments",
    "Start market launch"
  ]
}
```
