# 008 — Known Issues

## 1. QA Scenario Step Content

**Status**: UNRESOLVED (minor)

QA scenario steps in the database store `prompt` and `prompt_ru` fields but
the frontend renders `step.prompt_key`. When `prompt_key` is undefined, the
step content is not displayed.

**Root Cause**: QA scenario JSON files define steps with `prompt`/`prompt_ru`
rather than `prompt_key`. The `ScenarioStep` table is not used by the seed
script; steps are stored as raw JSON in the `Scenario.steps` column.

**Impact**: QA scenario users may not see the step prompt/instruction text.
The scenario title and goal ARE shown correctly.

**Fix**: Either add `prompt_key` to QA scenario step objects, or modify the
frontend to accept `prompt`/`prompt_ru` fields as fallbacks. This is a
secondary issue that doesn't block runtime recovery.

## 2. Trainer Name from DB

**Status**: MITIGATED

The backend `TrainerProduct.name` column stores the English name
("QA Engineer Interview Trainer"). The frontend now uses locale keys
(`trainer.{trainer_product_id}`) with fallback to the DB value,
so it's not a blocker. A backend-side localization would be cleaner.

## 3. Scenario API 404 on Railway

**Status**: CONFIGURATION ISSUE

The 404 error for scenario endpoints on Railway staging is caused by
missing/invalid `NEXT_PUBLIC_API_BASE_URL`. The frontend API client
code is correct; the Railway environment variable must be set.

## 4. Missing Dedicated Localization Audit CI Job

**Status**: NOT IMPLEMENTED

The CI workflow does not have a dedicated localization audit job.
This can be added as a separate step in the `frontend-tests` job.

## 5. No Browser E2E CI Job

**Status**: NOT IMPLEMENTED

The CI workflow does not have a browser E2E job against Railway staging.
This is documented as a future improvement.

## 6. Step Prompt Display on QA Scenario Detail Page

**Status**: MINOR UX ISSUE

When viewing a QA scenario detail page (`/scenarios/qa_*_v1`), the step
prompt content may not render because the step object lacks `prompt_key`.
The scenario title, goal, difficulty, duration, and skills all render correctly.
