# Phase 2 Scope Decision — BA Trainer AI Evaluation & Scenario Practice

## Decision

**AUTHORIZED** — Phase 2 is approved for implementation based on authoritative documentation review.

## Authoritative Documents Reviewed

| Document | Source | Findings |
|---|---|---|
| `docs/migrations/ba_trainer/migration_decision.md` | Migration pack | Non-blocking gaps include hybrid_evaluation, keyword_based_text_evaluation; Phase 2 authorized after Phase 1 |
| `docs/migrations/ba_trainer/migration_execution_plan.md` | Migration pack | Phase 2 tasks: AI rubrics, BA evaluation prompts, keyword pre-check, textarea question import, diagnostics, reports, analytics |
| `docs/migrations/ba_trainer/gap_analysis_and_priorities.md` | Migration pack | AI evaluation already_supported; BA-specific rubrics and scenarios are P0; 44 textarea questions pending |
| `docs/migrations/ba_trainer/evaluation_policy.md` | Migration pack | AI evaluation uses DeepSeek via AI Gateway for semantic tasks; rubrics with criteria, weights, levels |
| `docs/migrations/ba_trainer/native_trainer_pack_spec.md` | Migration pack | BA-specific rubrics, diagnostics, report aggregation; Phase 2 = version 0.3.0 |
| `docs/migrations/ba_trainer/platform_capability_mapping.md` | Migration pack | Open-text AI evaluation integration is Phase 2 blocking gap; BA rubrics/prompts needed |
| `docs/migrations/ba_trainer/source_product_review.md` | Migration pack | Source has 44 textarea questions requiring AI evaluation |
| `docs/migrations/ba_trainer/progress_diagnostics_exam_mapping.md` | Migration pack | Attempt → Evaluation → Progress pipeline already exists |
| `docs/migrations/ba_trainer/analytics_privacy_mapping.md` | Migration pack | Analytics events defined; raw answers forbidden in analytics |
| `docs/14.master_project_documentation_index.md` | Master index | Next allowed action is BA Phase 2 |
| `docs/migrations/ba_trainer/phase_1_implementation_report.md` | Phase 1 report | 164 activities, 10 modules, 5 deterministic types accepted |
| `docs/migrations/ba_trainer/phase_1_real_browser_acceptance_report.md` | Phase 1 report | Carryover: i18n keys visible, Playwright trace missing |

## Resolved Conflicts

| Conflict | Resolution |
|---|---|
| Phase 2 includes diagnostics vs. Phase 2 focuses on AI evaluation | **Resolution:** Phase 2 focuses ONLY on AI evaluation for scenario-based assignments. Diagnostics is deferred to Phase 3 per the explicit "Excludes" note in the migration execution plan Phase 2 section: "Excludes: Exam mode, advanced interactions, XP." Diagnostics is similarly deferred. |
| 44 textarea questions vs. scenario-based approach | **Resolution:** Phase 2 implements scenario-based assignments (not individual textarea questions). Each scenario presents a realistic BA task with business context, not a single textarea question. This aligns with the platform's existing Scenario model and delivers higher value. The 44 individual textarea questions remain Phase 3 candidates. |
| Phase 2 scope includes reporting | **Resolution:** Basic progress integration is in scope (scenario completion tracking). Full module-level report aggregation is deferred to Phase 3. |

## Scope Definition

```json
{
  "phase_2_learning_goal": "Enable realistic Business Analyst scenario practice with structured AI evaluation using DeepSeek. Learners receive rubric-based feedback on their analytical thinking, requirements engineering, process modeling, stakeholder management, and communication skills.",
  "phase_2_modules_or_scenarios": [
    "ba_phase2_stakeholder_requirements",
    "ba_phase2_process_analysis",
    "ba_phase2_documentation_artifacts",
    "ba_phase2_conflict_resolution",
    "ba_phase2_traceability_impact",
    "ba_phase2_real_case_analysis"
  ],
  "submission_formats": [
    "free_text"
  ],
  "evaluation_mode": "ai_only",
  "rubric_contract": "Each scenario has a rubric with 3-5 criteria. Each criterion has score 0-100. Total score = weighted average, max 100. Pass threshold = 70. Structured feedback includes criterion scores, evidence, strengths, improvement areas, and summary feedback.",
  "passing_policy": "Scenario is passed when overall_score >= 70. Passed scenarios increment completed_scenarios in progress. Failures increment total_attempts but not completed_scenarios.",
  "retry_policy": "No blind automatic retry. Learner may resubmit up to max_attempts (3) per scenario. Provider failures preserve submission state and require manual retry with justification. Frontend must not auto-retry on failure.",
  "progress_policy": "Total attempts increment exactly once per evaluation. Completed scenarios increment only on pass. Average score is rolling. All progress persists across refresh and relogin. Users are fully isolated.",
  "analytics_policy": "Record events: scenario_opened, scenario_started, submission_created, evaluation_completed, evaluation_failed, result_viewed, retry_requested. Never store raw submissions, authorization headers, tokens, or secrets in analytics. User identifiers minimized to user_id only.",
  "out_of_scope": [
    "Diagnostics assessment flow",
    "Module-level progress report aggregation",
    "Exam mode with timer",
    "Advanced interaction components (drag-sort, interactive board, etc.)",
    "XP / gamification",
    "English (en-US) locale for BA content",
    "44 individual textarea questions from source (deferred to Phase 3)",
    "Drag-sort and matching for Phase 2 scenarios (free-text only)",
    "Production deployment or release",
    "Payments, marketplace, B2B dashboard",
    "Modifying QA Trainer content or runtime"
  ]
}
```

## Implementation Strategy

Phase 2 reuses the platform's existing **Scenario runtime** + **AI Evaluation** infrastructure with DeepSeek. No new backend modules are required. The work consists of:

1. **BA Phase 2 scenario content** — New scenarios with BA-specific context, tasks, constraints, and rubrics
2. **Frontend pages** — Phase 2 scenario list and runner integrated into the BA Trainer
3. **Progress integration** — Wire existing ProgressService to BA Phase 2 scenarios
4. **Analytics events** — Register Phase 2-specific event types
5. **Retry policy** — Enforce max_attempts and disable blind retry
6. **i18n fix** — Replace raw translation keys with translated text (Phase 1 carryover)

## Authorization

```json
{
  "authorized": true,
  "authorized_by": "Documentation review of migration_decision.md, migration_execution_plan.md, gap_analysis_and_priorities.md, native_trainer_pack_spec.md",
  "phase_2_scenarios_count": 6,
  "max_attempts_default": 3,
  "pass_threshold": 70,
  "ai_provider": "deepseek",
  "ai_model": "deepseek-v4-flash",
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": "implement_ba_phase_2"
}
```
