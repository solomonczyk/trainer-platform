# Railway Migration and Seed Report

## Migrations

**Date**: 2026-06-05
**Target**: Railway PostgreSQL (staging environment)

### Migration Applied

| Revision | Name                                           | Status |
|----------|------------------------------------------------|--------|
| `001`    | Initial MVP schema — create all platform tables| ✅     |

### Schema Verification

**27 tables created:**

- `users`, `user_profiles`
- `domains`, `trainer_products`, `trainer_versions`, `trainer_localizations`
- `tracks`, `modules`
- `scenarios`, `scenario_steps`
- `skill_maps`, `skills`
- `rubrics`, `rubric_criteria`, `critical_errors`
- `user_trainer_enrollments`, `simulation_sessions`, `simulation_messages`, `attempts`
- `evaluations`, `evaluation_criteria_results`
- `trainer_progress`, `skill_scores`
- `analytics_events`, `ai_requests`
- `feature_flags`
- `alembic_version`

### Migration Command
```bash
cd backend
DATABASE_URL="postgresql+asyncpg://..." alembic upgrade head
```

## Seed Data

### QA Engineer Interview Trainer

| Check                          | Value         | Status |
|--------------------------------|---------------|--------|
| IT Domain exists               | `it`          | ✅     |
| QA Engineer Trainer exists     | `qa-engineer-interview-trainer` | ✅ |
| Trainer version                | `1.0.0`       | ✅     |
| Scenarios count                | 5             | ✅     |
| Locales                        | ru-RU, en-US  | ✅     |
| Rubrics                        | 5             | ✅     |
| Skill maps                     | 1             | ✅     |
| Critical errors                | 4             | ✅     |
| Admin user                     | admin@trainerplatform.com | ✅ |

### Seed Scenarios

1. `qa_bug_report_structure_v1`
2. `qa_login_form_testing_v1`
3. `qa_regression_vs_retest_v1`
4. `qa_self_presentation_v1`
5. `qa_test_case_vs_checklist_v1`

### Seed Command
```bash
cd backend
DATABASE_URL="postgresql+asyncpg://..." python3 scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer
```
