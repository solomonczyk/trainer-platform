# TRAINER-PLATFORM-MVP-001
# Core Platform + QA Engineer Interview Trainer Vertical Slice

**Версия:** 1.0  
**Дата:** 03.06.2026  
**Статус:** Ready for Engineering Agent / Development Start  
**Тип задачи:** Full vertical feature-layer  
**Проект:** Trainer Platform — платформа самодостаточных профессиональных тренажеров  
**Первый MVP-тренажер:** QA Engineer Interview Trainer  
**Режим MVP:** text-only  
**Локали MVP:** ru-RU, en-US  

---

# 0. Executive Summary

## 0.1. Что нужно сделать

Реализовать первый рабочий vertical slice платформы:

```text
Platform Core
+ IT Domain
+ QA Engineer Interview Trainer
+ Scenario Runtime
+ Attempt Persistence
+ Rubric-based AI Evaluation
+ Progress Tracking
+ Analytics
+ Basic Admin/Seed/Health
+ CI/Tests/Proof
```

MVP должен доказать, что система является **платформой самодостаточных trainer products**, а не просто сайтом с одним QA-тренажером.

---

## 0.2. Главная цель

Создать минимально полноценную платформенную основу, на которой пользователь может:

```text
зарегистрироваться / войти
→ выбрать язык
→ открыть домен IT
→ открыть QA Engineer Interview Trainer
→ enroll в тренажер
→ выбрать сценарий
→ пройти text-сценарий
→ сохранить attempt
→ получить AI evaluation по рубрике
→ увидеть score, evidence, weak points, next action
→ увидеть progress по тренажеру
→ повторить сценарий
```

---

## 0.3. Главный архитектурный принцип

```text
Platform Core ≠ QA Trainer
```

QA Engineer Interview Trainer — это **первый trainer product**, загруженный как seed trainer package.

Платформа должна быть готова позже принять другие trainer products:

```text
Prompt Engineer Trainer
Python Developer Trainer
Sales Trainer
English for Work Trainer
Customer Support Trainer
Cybersecurity Trainer
```

Но в этом layer реализуется только QA Engineer Interview Trainer.

---

# 1. Source of Truth

Исполнитель должен опираться на документы проекта:

```text
01 Product Owner Documentation Pack
02 Business Analyst Documentation Pack
03 Product Manager Documentation Pack
04 System / Solution Architect Documentation Pack
05 UX/UI Designer Documentation Pack
06 Learning Experience Designer Documentation Pack
07 Domain Expert Documentation Pack
08 AI / LLM Architect Documentation Pack
09 Data / Analytics Specialist Documentation Pack
10 Security / Legal / Compliance Documentation Pack
11 QA Lead Documentation Pack
12 DevOps / Infrastructure Engineer Documentation Pack
13 Engineering Lead / Development Standards Documentation Pack
14 Master Project Documentation Index v0.2
15 Implementation Task Specification v0.2 Addendum
16 MVP Acceptance & Release Readiness Plan
17 Documentation Gap Analysis & Corrective Addendum
18 Backend Engineering Specification
19 Frontend Engineering Specification
20 Trainer Package Schema Specification
21 OpenAPI / API Contract Specification
22 Auth / RBAC / Access Control Specification
23 Admin / Backoffice MVP Specification
24 Seed Data & Migration Runbook
25 Prompt Registry & Model Operations Specification
26 AI Evaluation Calibration Report
27 UI Design System / Component Library Specification
28 Accessibility & Inclusive UX Specification
29 Beta Testing & User Feedback Plan
30 Feature Flags / Rollout / Kill Switch Plan
31 AI Cost Budget & Unit Economics Guardrail
32 Documentation Governance & Versioning Plan
33 NFR / SLO / Performance & Reliability Specification
```

Если есть конфликт между документами, использовать исправленный baseline:

```json
{
  "first_domain": "IT",
  "first_trainer_product": "QA Engineer Interview Trainer",
  "prompt_engineer_trainer": "later_or_portfolio_alternative",
  "mvp_mode": "text_only",
  "locales": ["ru-RU", "en-US"],
  "architecture": "modular_monolith_first",
  "backend": "FastAPI",
  "frontend": "Next.js + TypeScript",
  "database": "PostgreSQL",
  "ai_layer": "AI Gateway + Prompt Registry + Structured Evaluation",
  "evaluation": "rubric_based_json_with_evidence",
  "progress": "per_user_per_trainer_product",
  "analytics": "event_based_from_mvp"
}
```

---

# 2. Goal

## 2.1. Product Goal

Создать MVP, который доказывает продуктовую модель:

```text
Platform
→ Domain
→ Trainer Product
→ Trainer Version
→ Scenario
→ Attempt
→ Evaluation
→ Progress
```

## 2.2. Engineering Goal

Реализовать deployable MVP vertical slice:

```text
Frontend Next.js
+ FastAPI backend
+ PostgreSQL schema
+ trainer package seed
+ scenario runtime
+ AI Gateway
+ evaluation validation
+ progress engine
+ analytics
+ admin health/seed status
+ tests
+ proof JSON
```

## 2.3. Learning Goal

Пользователь должен не просто получить ответ от AI, а пройти тренировочный цикл:

```text
context
→ user answer
→ rubric evaluation
→ evidence-based feedback
→ weak points
→ retry / next recommendation
→ progress update
```

---

# 3. Allowed Scope

В рамках этого layer разрешено реализовать:

## 3.1. Frontend

```text
Next.js app shell
landing page
login/register or MVP auth flow
domain catalog
domain page: IT
trainer product page: QA Engineer Interview Trainer
enrollment modal/flow
scenario list
scenario intro
scenario runner
evaluation loading state
result page
progress dashboard/page
profile/settings minimal
admin seed/status MVP-lite
language switcher ru-RU/en-US
frontend analytics client
```

## 3.2. Backend

```text
FastAPI modular monolith
config module
database connection
Alembic migrations
health/ready endpoints
auth/current user
domain catalog API
trainer registry API
trainer package seed
scenario runtime API
attempt persistence
evaluation runtime
progress engine
analytics event API
admin seed/status API
OpenAPI export
```

## 3.3. Database

```text
users
user_profiles
domains
trainer_products
trainer_versions
trainer_localizations
tracks
modules
scenarios
scenario_steps
skill_maps
skills
rubrics
rubric_criteria
critical_errors
user_trainer_enrollments
simulation_sessions
simulation_messages
attempts
evaluations
evaluation_criteria_results
trainer_progress
skill_scores
analytics_events
ai_requests
feature_flags if used
admin_audit_logs if used
```

## 3.4. Trainer Package

Seed package:

```text
Domain: IT
Trainer Product: QA Engineer Interview Trainer
Trainer Version: 1.0.0
Locales: ru-RU, en-US
Mode: text-only
```

Minimum scenarios:

```text
1. Tell about yourself as QA candidate
2. Test case vs checklist
3. Bug report structure
4. Regression vs retest
5. Login form testing
```

Package must include:

```text
trainer metadata
trainer version
skill map
rubric pack
critical errors
scenario pack
locale packs ru/en
golden answer set
validation cases
```

## 3.5. AI Layer

```text
AI Gateway
provider adapter interface
mock provider for tests
real provider adapter configurable
Prompt Registry
evaluator_prompt_qa_interview_v1
evaluation_contract_v1
structured JSON validation
score range validation
evidence validation
critical error blocking
AI request logging
cost metadata
timeout handling
invalid JSON handling
feature flag to disable AI evaluation
```

## 3.6. Analytics

Required events:

```text
user_registered
user_logged_in
locale_changed
domain_catalog_viewed
domain_viewed
trainer_viewed
trainer_enroll_clicked
trainer_enrolled
scenario_list_viewed
scenario_viewed
scenario_started
answer_submitted
attempt_completed
evaluation_requested
evaluation_received
evaluation_failed
evaluation_result_viewed
scenario_completed
retry_started
progress_updated
progress_viewed
ai_request_started
ai_request_completed
ai_request_failed
```

Analytics must not contain:

```text
raw answer text
full transcript
passwords
tokens
AI API keys
payment data
```

---

# 4. Forbidden Actions

The agent/developer must not do the following:

```text
do not implement Prompt Engineer Trainer as MVP baseline
do not implement voice mode
do not implement marketplace
do not implement B2B organization dashboard
do not implement payment production integration
do not implement medical/legal/finance/cybersecurity production trainer
do not build one hardcoded QA-only app without trainer product abstraction
do not create free AI chat instead of scenario runtime
do not call LLM provider directly outside AI Gateway
do not store progress only in localStorage
do not store raw answers in analytics event properties
do not allow PASS when critical error is detected
do not score without evidence
do not use free-form AI text as source of truth
do not skip evaluation JSON validation
do not lose attempt when AI provider fails
do not expose secrets in frontend
do not skip migrations
do not skip tests
do not skip proof JSON
do not mark production_accepted=true
```

---

# 5. Required Architecture

## 5.1. High-Level Architecture

```text
[Next.js Frontend]
        |
        v
[FastAPI Modular Monolith]
        |
        +--> Auth/User Module
        +--> Domain Catalog Module
        +--> Trainer Registry Module
        +--> Trainer Package Module
        +--> Scenario Runtime Module
        +--> Evaluation Runtime Module
        +--> Progress Engine Module
        +--> Localization Module
        +--> Analytics Module
        +--> Admin/Seed Module
        +--> AI Gateway Module
        |
        v
[PostgreSQL]
        |
        v
[External AI Provider through AI Gateway]
```

## 5.2. Backend Module Boundaries

```text
routers → services → repositories → database
services → AI Gateway
AI Gateway → provider adapters
```

Forbidden:

```text
business logic in routers
LLM SDK inside evaluation service
raw SQL without reason
frontend hardcoding trainer internals
```

## 5.3. Frontend Architecture

```text
app routes
feature modules
typed API client
centralized error handling
i18n layer
analytics client
protected route guard
component library
```

---

# 6. Required User Journey

The full MVP journey must work:

```text
1. User opens landing.
2. User registers or logs in.
3. User selects ru-RU or en-US.
4. User opens domain catalog.
5. User opens IT domain.
6. User opens QA Engineer Interview Trainer.
7. User enrolls in trainer.
8. User sees scenario list.
9. User opens Bug Report Structure scenario.
10. User sees scenario intro.
11. User starts scenario.
12. System creates simulation_session and attempt.
13. User submits answer.
14. System saves answer as simulation_message.
15. User completes attempt.
16. System saves attempt before AI call.
17. Evaluation Runtime calls AI Gateway.
18. AI Gateway uses evaluator prompt and returns structured JSON.
19. System validates evaluation.
20. System stores evaluation and criterion results.
21. System updates progress and skill scores.
22. User sees result page.
23. User can retry or open progress page.
24. Analytics events and AI request logs are recorded.
```

---

# 7. Required Implementation

---

## EPIC-001 — Project Foundation

### Goal

Создать базовую структуру проекта.

### Required

```text
repository structure
frontend app
backend app
docker-compose local PostgreSQL
.env.example
README
Makefile or task scripts
basic local start commands
```

### Artifacts

```text
README.md
.env.example
docker-compose.local.yml
Makefile or package scripts
frontend/
backend/
trainer_packages/
docs/
scripts/
```

### Acceptance

```json
{
  "repo_structure_created": true,
  "local_env_documented": true,
  "frontend_starts": true,
  "backend_starts": true,
  "database_starts": true
}
```

---

## EPIC-002 — Backend Foundation

### Goal

FastAPI backend foundation.

### Required

```text
FastAPI app
config module
database module
structured logging
request_id middleware
health endpoint
ready endpoint
OpenAPI enabled
global error handler
```

### Endpoints

```text
GET /health
GET /ready
GET /openapi.json
```

### Acceptance

```json
{
  "fastapi_app_created": true,
  "health_endpoint_works": true,
  "ready_endpoint_works": true,
  "openapi_available": true,
  "global_error_format_enabled": true
}
```

---

## EPIC-003 — Database Schema & Migrations

### Goal

Создать MVP schema.

### Required tables

```text
users
user_profiles
domains
trainer_products
trainer_versions
trainer_localizations
tracks
modules
scenarios
scenario_steps
skill_maps
skills
rubrics
rubric_criteria
critical_errors
user_trainer_enrollments
simulation_sessions
simulation_messages
attempts
evaluations
evaluation_criteria_results
trainer_progress
skill_scores
analytics_events
ai_requests
feature_flags
```

### Required

```text
Alembic migrations
migration command
migration rollback note
schema tests
```

### Acceptance

```json
{
  "migrations_created": true,
  "migrations_run_cleanly": true,
  "tables_created": true,
  "rollback_documented": true
}
```

---

## EPIC-004 — Auth / User Profile / RBAC

### Goal

Создать MVP auth и user ownership.

### Required

```text
register/login or MVP auth provider integration
current user endpoint
profile update
preferred locale
roles: guest, registered_user, admin, system_service
protected routes
ownership checks
```

### Required endpoints

```text
GET /api/v1/me
PATCH /api/v1/me
```

If custom auth:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
```

### Security rules

```text
user can access only own attempts
user can access only own evaluations
user can access only own progress
non-admin cannot access admin routes
```

### Acceptance

```json
{
  "auth_flow_works": true,
  "current_user_endpoint_works": true,
  "preferred_locale_saved": true,
  "rbac_enabled": true,
  "ownership_checks_pass": true
}
```

---

## EPIC-005 — Trainer Package Schema + Seed

### Goal

Создать канонический seed package первого тренажера.

### Required package

```text
trainer_packages/qa_engineer_interview_trainer/
├── trainer.json
├── trainer_version.json
├── skill_map.json
├── rubric_pack.json
├── critical_errors.json
├── scenarios/
├── locales/
├── golden_answers/
└── package_tests/
```

### Required scenarios

```text
qa_self_presentation_v1
qa_test_case_vs_checklist_v1
qa_bug_report_structure_v1
qa_regression_vs_retest_v1
qa_login_form_testing_v1
```

### Required skills

```text
interview_structure
communication_clarity
self_presentation
qa_terms
test_documentation
bug_reporting
test_design
practical_reasoning
uncertainty_handling
```

### Required critical errors

```text
qa_crit_no_understanding_qa_role
qa_crit_steps_to_reproduce_not_needed
qa_crit_only_happy_path_testing
qa_crit_confuse_actual_expected
qa_crit_hide_bugs
qa_crit_fake_experience
qa_crit_no_need_requirements
qa_crit_test_prod_without_permission
```

### Required

```text
package validator
idempotent seed script
pre-seed validation
post-seed validation
```

### Acceptance

```json
{
  "trainer_package_created": true,
  "qa_trainer_seeded": true,
  "scenarios_seeded": 5,
  "rubrics_seeded": true,
  "skill_map_seeded": true,
  "locales_seeded": ["ru-RU", "en-US"],
  "critical_errors_seeded": true,
  "package_validation_passed": true,
  "seed_is_idempotent": true
}
```

---

## EPIC-006 — Domain & Trainer Catalog

### Goal

Показать платформенную модель: Domain → Trainer Product.

### Backend endpoints

```text
GET /api/v1/domains
GET /api/v1/domains/{domain_slug}
GET /api/v1/trainers/{trainer_slug}
```

### Frontend routes

```text
/domains
/domains/[domainSlug]
/trainers/[trainerSlug]
```

### Required UI

```text
Domain Catalog
IT Domain Page
QA Engineer Interview Trainer Product Page
```

### Acceptance

```json
{
  "domain_catalog_works": true,
  "it_domain_page_works": true,
  "qa_trainer_page_works": true,
  "trainer_product_not_hardcoded_as_only_app": true
}
```

---

## EPIC-007 — Enrollment

### Goal

Пользователь enrolls в trainer product, progress создается отдельно по trainer.

### Endpoint

```text
POST /api/v1/trainers/{trainer_slug}/enroll
```

### Required behavior

```text
registered user only
idempotent enrollment
create user_trainer_enrollment
create trainer_progress
record trainer_enrolled event
```

### Acceptance

```json
{
  "enrollment_works": true,
  "enrollment_idempotent": true,
  "trainer_progress_created": true,
  "trainer_enrolled_event_recorded": true
}
```

---

## EPIC-008 — Scenario List & Scenario Intro

### Goal

Пользователь видит сценарии внутри QA trainer.

### Backend endpoints

```text
GET /api/v1/trainers/{trainer_slug}/scenarios
GET /api/v1/scenarios/{scenario_id}
```

### Frontend routes

```text
/trainers/[trainerSlug]/scenarios
/scenarios/[scenarioId]
```

### Required

```text
scenario cards
difficulty
estimated duration
last score if exists
status
start CTA
scenario context
evaluation preview
skills trained
```

### Acceptance

```json
{
  "scenario_list_works": true,
  "scenario_intro_works": true,
  "scenario_content_localized": true,
  "skills_displayed": true
}
```

---

## EPIC-009 — Scenario Runtime

### Goal

Пользователь проходит text scenario.

### Endpoints

```text
POST /api/v1/scenarios/{scenario_id}/start
POST /api/v1/sessions/{session_id}/messages
POST /api/v1/sessions/{session_id}/complete
```

### Required behavior

```text
start creates simulation_session
start creates attempt
submit answer saves simulation_message
empty answer blocked
complete marks attempt completed
attempt saved before evaluation
refresh recovery handled or safely messaged
```

### Frontend route

```text
/scenarios/[scenarioId]/run
```

### Acceptance

```json
{
  "scenario_start_creates_session": true,
  "scenario_start_creates_attempt": true,
  "answer_saved": true,
  "empty_answer_blocked": true,
  "attempt_completed": true,
  "attempt_saved_before_ai": true
}
```

---

## EPIC-010 — AI Gateway + Prompt Registry

### Goal

Все AI-вызовы проходят через AI Gateway.

### Required

```text
AI Gateway service
provider adapter interface
mock provider
configurable real provider adapter
Prompt Registry
evaluator_prompt_qa_interview_v1
evaluation_contract_v1
structured output validation
timeout handling
retry policy max 1
fallback policy placeholder
AI request logging
cost metadata
```

### Forbidden

```text
direct provider SDK calls outside AI Gateway
unbounded retry
unlogged AI request
```

### Required AI Gateway request

```json
{
  "task_type": "rubric_evaluation",
  "trainer_product_id": "qa_engineer_interview_trainer",
  "trainer_version": "1.0.0",
  "scenario_id": "qa_bug_report_structure_v1",
  "attempt_id": "uuid",
  "locale": "ru-RU",
  "prompt_template_id": "evaluator_prompt_qa_interview_v1",
  "prompt_version": "1.0.0",
  "input": {
    "scenario_context": {},
    "rubric": {},
    "transcript": [],
    "domain_rules": {},
    "critical_errors": []
  },
  "output_schema_id": "evaluation_contract_v1"
}
```

### Acceptance

```json
{
  "ai_gateway_created": true,
  "mock_provider_available": true,
  "real_provider_configurable": true,
  "prompt_registry_created": true,
  "evaluator_prompt_v1_registered": true,
  "ai_request_logged": true,
  "cost_metadata_logged": true,
  "no_direct_llm_calls_outside_gateway": true
}
```

---

## EPIC-011 — Evaluation Runtime

### Goal

Оценить attempt по рубрике и сохранить structured result.

### Endpoints

```text
POST /api/v1/attempts/{attempt_id}/evaluate
GET /api/v1/attempts/{attempt_id}/evaluation
```

### Required evaluation output

```json
{
  "overall_score": 0,
  "passed": false,
  "criteria": [
    {
      "criterion_id": "technical_accuracy",
      "score": 0,
      "evidence": "",
      "comment": "",
      "improvement": ""
    }
  ],
  "strengths": [],
  "weak_points": [],
  "critical_errors": [],
  "next_recommendation": {},
  "confidence": 0.0
}
```

### Validation rules

```text
JSON schema valid
all rubric criteria present
score range 0–100
criteria weights respected
evidence required
critical error blocks passed=true
locale valid
no invented evidence if detectable
```

### Failure behavior

```text
invalid JSON → evaluation_failed, attempt preserved
timeout → evaluation_failed, attempt preserved
safety violation → evaluation_blocked, attempt preserved
cost limit exceeded → evaluation_blocked, attempt preserved
```

### Acceptance

```json
{
  "evaluation_endpoint_works": true,
  "evaluation_json_validated": true,
  "criteria_results_stored": true,
  "evidence_required": true,
  "critical_error_blocks_pass": true,
  "invalid_json_safe_failure": true,
  "timeout_safe_failure": true,
  "attempt_preserved_on_ai_failure": true
}
```

---

## EPIC-012 — Result Page

### Goal

Пользователь видит понятную оценку.

### Required UI

```text
overall score
passed / needs practice
criteria breakdown
evidence per criterion
strengths
weak points
critical errors
next recommendation
retry CTA
progress updated note
```

### UX rules

```text
do not shame user
show critical errors clearly
show next action
score not color-only
loading/evaluation_failed states included
```

### Acceptance

```json
{
  "result_page_works": true,
  "score_displayed": true,
  "criteria_breakdown_displayed": true,
  "evidence_displayed": true,
  "critical_errors_displayed": true,
  "next_recommendation_displayed": true,
  "retry_cta_available": true
}
```

---

## EPIC-013 — Progress Engine

### Goal

Хранить и показывать progress per trainer product.

### Required

```text
create progress on enrollment
update progress after evaluation
update skill_scores
calculate average score
calculate completed scenarios
calculate readiness status
recommend next scenario or retry
```

### Endpoint

```text
GET /api/v1/me/progress
GET /api/v1/me/progress/{trainer_slug}
```

### Frontend

```text
/me/progress
/me/progress/[trainerSlug]
```

### Readiness statuses

```text
not_started
in_progress
needs_practice
almost_ready
ready
strong
```

### Acceptance

```json
{
  "progress_created_on_enrollment": true,
  "progress_updated_after_evaluation": true,
  "skill_scores_updated": true,
  "readiness_status_calculated": true,
  "progress_page_works": true,
  "progress_is_per_trainer_product": true
}
```

---

## EPIC-014 — Localization

### Goal

MVP работает на ru-RU и en-US.

### Required

```text
UI strings ru/en
trainer content ru/en
scenario content ru/en
result labels ru/en
evaluation prompt locale variable
fallback rule
```

### Rules

```text
selected locale affects UI
selected locale affects trainer/scenario content
selected locale affects AI feedback
missing P0 locale blocks publication or uses safe fallback
```

### Acceptance

```json
{
  "ru_ru_flow_works": true,
  "en_us_flow_works": true,
  "locale_switch_works": true,
  "trainer_content_localized": true,
  "scenario_content_localized": true,
  "evaluation_feedback_locale_controlled": true
}
```

---

## EPIC-015 — Analytics

### Goal

Собирать privacy-safe product, learning and AI events.

### Required backend

```text
analytics_events table
analytics event API
backend event recorder
frontend analytics client
AI request logging
```

### Required privacy rule

```text
reject or sanitize analytics event containing raw_answer, transcript, password, token, api_key
```

### Acceptance

```json
{
  "analytics_events_recorded": true,
  "trainer_context_present": true,
  "scenario_context_present": true,
  "ai_cost_logged": true,
  "raw_answers_not_in_analytics": true,
  "core_funnel_calculable": true
}
```

---

## EPIC-016 — Admin MVP-lite

### Goal

Минимальный admin для проверки состояния MVP.

### Routes

```text
/admin
/admin/seed-status
/admin/trainers
/admin/evaluations/failures
/admin/analytics/sanity
/admin/system-health
```

### Required

```text
admin-only access
seed status
trainer package validation status
scenario/rubric/locale counts
AI failure list without raw answers by default
analytics sanity counts
system health
```

### Acceptance

```json
{
  "admin_routes_protected": true,
  "seed_status_visible": true,
  "trainer_validation_status_visible": true,
  "ai_failures_visible_without_raw_answers": true,
  "analytics_sanity_visible": true,
  "system_health_visible": true
}
```

---

## EPIC-017 — Feature Flags / Kill Switch

### Goal

Можно отключить опасную часть без потери данных.

### Required flags

```text
trainer.qa_interview.visible
trainer.qa_interview.enrollment_enabled
scenario_runtime.enabled
ai_evaluation.enabled
ai_evaluation.real_provider_enabled
analytics.enabled
locale.en_us.enabled
beta_access.enabled
```

### Required behavior

```text
if AI evaluation disabled → attempt still saved, evaluation temporarily unavailable
if trainer hidden → existing attempts accessible, new starts blocked
if locale disabled → fallback or blocked safely
```

### Acceptance

```json
{
  "feature_flags_present": true,
  "ai_evaluation_can_be_disabled": true,
  "attempt_saved_when_ai_disabled": true,
  "trainer_visibility_can_be_disabled": true,
  "flag_changes_auditable_or_logged": true
}
```

---

## EPIC-018 — Security / Privacy Baseline

### Required

```text
user data ownership checks
admin route protection
no secrets in frontend
AI request data minimization
raw answers not in analytics
safe interview disclaimer
rate limit placeholder or basic implementation
```

### Required tests

```text
user A cannot read user B attempt
user A cannot read user B evaluation
guest cannot access progress
non-admin cannot access admin
analytics rejects raw answer
```

### Acceptance

```json
{
  "user_data_isolation_passed": true,
  "admin_routes_protected": true,
  "no_secrets_in_frontend": true,
  "raw_answers_not_in_analytics": true,
  "ai_data_minimized": true,
  "interview_disclaimer_visible": true
}
```

---

## EPIC-019 — NFR / SLO Baseline

### Required

```text
attempt saved before AI
health/ready checks
evaluation timeout
controlled AI failure
basic latency measurement
AI cost tracking
backup/rollback docs
```

### MVP targets

```text
catalog p95 <= 800ms in local/staging smoke
answer submit p95 <= 1500ms in local/staging smoke
evaluation timeout <= 30s
attempt loss = 0
cross-user access = 0
critical error pass = 0
raw answer analytics violation = 0
```

### Acceptance

```json
{
  "health_ready_checks_work": true,
  "attempt_loss_allowed": 0,
  "ai_timeout_controlled": true,
  "basic_latency_logged": true,
  "ai_cost_logged": true,
  "rollback_docs_exist": true,
  "backup_docs_exist": true
}
```

---

## EPIC-020 — Tests

### Required test groups

```text
backend unit tests
API tests
DB/migration tests
trainer package validation tests
scenario runtime tests
AI Gateway mock tests
evaluation contract tests
critical error tests
progress tests
analytics privacy tests
RBAC/security tests
localization tests
frontend component/page tests
E2E smoke test
```

### Required golden answer cases

```text
excellent answer
good answer
medium answer
bad answer
critical answer
empty answer
off-topic answer
prompt injection answer
```

### Required test examples

```text
test_health_ready
test_user_registration_login
test_domain_trainer_catalog
test_trainer_enrollment_idempotent
test_scenario_start_creates_session_attempt
test_submit_answer_saves_message
test_attempt_saved_before_ai_failure
test_evaluation_contract_valid
test_invalid_ai_json_safe_failure
test_critical_error_blocks_pass
test_progress_update_after_evaluation
test_no_raw_answer_in_analytics
test_user_cannot_access_other_user_attempt
test_ru_en_localization
test_feature_flag_disable_ai_evaluation
test_frontend_build
test_e2e_main_flow
```

### Acceptance

```json
{
  "backend_tests_pass": true,
  "frontend_tests_pass": true,
  "api_tests_pass": true,
  "ai_contract_tests_pass": true,
  "critical_error_tests_pass": true,
  "analytics_privacy_tests_pass": true,
  "security_tests_pass": true,
  "e2e_smoke_pass": true
}
```

---

## EPIC-021 — DevOps / CI / Local Run

### Required

```text
local start command
docker-compose local PostgreSQL
.env.example
backend test command
frontend build command
migration command
seed command
CI pipeline definition
health checks
rollback notes
backup notes
```

### CI required checks

```text
backend lint/test
frontend lint/typecheck/build
migration check
trainer package validation
AI contract tests with mock provider
analytics privacy tests
```

### Acceptance

```json
{
  "local_start_documented": true,
  "docker_compose_postgres_works": true,
  "env_example_exists": true,
  "ci_defined": true,
  "frontend_build_passed": true,
  "backend_tests_passed": true,
  "migration_command_documented": true,
  "seed_command_documented": true
}
```

---

# 8. Control Points

The implementation must produce evidence for each control point:

```text
CP-001 repo structure created
CP-002 local env works
CP-003 migrations run cleanly
CP-004 seed package validates
CP-005 QA trainer seeded
CP-006 OpenAPI schema exported
CP-007 auth/current user works
CP-008 domain/trainer catalog works
CP-009 enrollment idempotent
CP-010 scenario runtime creates session/attempt
CP-011 answer submission persists message
CP-012 attempt saved before AI
CP-013 AI Gateway used
CP-014 evaluation contract validates
CP-015 critical error blocks PASS
CP-016 result page renders evaluation
CP-017 progress updates per trainer product
CP-018 analytics events recorded
CP-019 raw answers absent from analytics
CP-020 AI request cost logged
CP-021 user isolation tests pass
CP-022 localization ru/en works
CP-023 feature flag disables AI safely
CP-024 admin seed/status works
CP-025 health/ready works
CP-026 frontend build passes
CP-027 backend tests pass
CP-028 E2E smoke passes
CP-029 proof JSON created
```

---

# 9. Required Artifacts

Implementation must create/update:

```text
README.md
.env.example
docker-compose.local.yml
Makefile or task scripts

frontend/
backend/
trainer_packages/qa_engineer_interview_trainer/

backend migrations
backend OpenAPI schema
backend tests
frontend tests
E2E smoke test

docs/implementation/TRAINER-PLATFORM-MVP-001.md
docs/proofs/proof_trainer_platform_mvp_001.json
docs/release/mvp_001_readiness_report.md
docs/known_issues/mvp_001_known_issues.md
```

If project uses different folders, equivalent artifacts are allowed, but proof must state actual paths.

---

# 10. Verification Commands

Agent must provide actual commands used.

Expected examples:

```bash
# backend
cd backend
python -m pytest

# migrations
alembic upgrade head

# seed
python scripts/validate_trainer_package.py trainer_packages/qa_engineer_interview_trainer
python scripts/seed_trainer_package.py trainer_packages/qa_engineer_interview_trainer

# frontend
cd frontend
npm install
npm run lint
npm run typecheck
npm run build
npm test

# e2e
npm run test:e2e

# local run
docker compose -f docker-compose.local.yml up
```

If commands differ, proof must include actual commands.

---

# 11. Acceptance Gates

## Gate 1 — Product Scope Gate

PASS if:

```text
MVP = Platform Core + IT Domain + QA Engineer Interview Trainer
Prompt Engineer not implemented as MVP baseline
voice not included
marketplace not included
B2B dashboard not included
trainer product abstraction preserved
```

FAIL if:

```text
system is just hardcoded QA site
```

---

## Gate 2 — Functional Gate

PASS if:

```text
register/login works
domain catalog works
trainer page works
enrollment works
scenario list works
scenario runner works
answer submission works
attempt saved
evaluation generated
result shown
progress updated
retry available or safely handled
```

---

## Gate 3 — AI Evaluation Gate

PASS if:

```text
AI Gateway used
evaluation contract valid
criteria complete
score within range
evidence present
critical errors block PASS
invalid JSON handled safely
timeout handled safely
prompt injection does not override rubric
```

FAIL if:

```text
score without evidence
PASS with critical error
invented feedback accepted as truth
direct LLM call outside AI Gateway
```

---

## Gate 4 — Learning Quality Gate

PASS if:

```text
trainer has skill map
scenarios mapped to skills
rubrics mapped to criteria
feedback gives next action
progress updates per skill
readiness status calculated
```

---

## Gate 5 — Analytics Gate

PASS if:

```text
core events recorded
trainer context present
scenario context present
AI cost logged
raw answers not in analytics
basic funnel calculable
```

---

## Gate 6 — Security / Privacy Gate

PASS if:

```text
users access only own data
admin routes protected
no secrets in frontend
raw answers not in analytics
AI request minimizes personal data
```

---

## Gate 7 — Localization Gate

PASS if:

```text
ru-RU P0 flow works
en-US P0 flow works
trainer/scenario/result localized
fallback deterministic
```

---

## Gate 8 — DevOps / Release Gate

PASS if:

```text
CI defined
frontend build passes
backend tests pass
migrations pass
health check works
rollback documented
backup documented
env/secrets documented
```

---

## Gate 9 — QA Gate

PASS if:

```text
main E2E smoke passed
API tests passed
AI golden set tests passed with mock/controlled cases
security/privacy tests passed
localization tests passed
analytics tests passed
no critical/high bugs open
```

---

## Gate 10 — Documentation Gate

PASS if:

```text
README updated
.env.example exists
proof JSON exists
known issues documented
implementation report exists
OpenAPI exported
```

---

# 12. Required Proof JSON

Create:

```text
docs/proofs/proof_trainer_platform_mvp_001.json
```

Required structure:

```json
{
  "layer": "TRAINER-PLATFORM-MVP-001",
  "title": "Core Platform + QA Engineer Interview Trainer Vertical Slice",
  "date": "YYYY-MM-DD",
  "verdict": "TBD",
  "source_docs_used": [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14_v0.2",
    "15_v0.2",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "30",
    "31",
    "33"
  ],
  "scope": {
    "first_domain": "IT",
    "first_trainer_product": "QA Engineer Interview Trainer",
    "prompt_engineer_trainer_included": false,
    "voice_mode_included": false,
    "marketplace_included": false,
    "b2b_dashboard_included": false,
    "platform_model_preserved": true
  },
  "implementation": {
    "frontend_created": false,
    "backend_created": false,
    "database_migrations_created": false,
    "trainer_package_created": false,
    "trainer_package_validated": false,
    "qa_trainer_seeded": false,
    "auth_implemented": false,
    "rbac_implemented": false,
    "domain_catalog_implemented": false,
    "trainer_catalog_implemented": false,
    "enrollment_implemented": false,
    "scenario_runtime_implemented": false,
    "attempt_persistence_implemented": false,
    "ai_gateway_implemented": false,
    "prompt_registry_implemented": false,
    "evaluation_runtime_implemented": false,
    "progress_engine_implemented": false,
    "analytics_implemented": false,
    "admin_mvp_implemented": false,
    "feature_flags_implemented": false,
    "localization_ru_en_implemented": false
  },
  "critical_controls": {
    "attempt_saved_before_ai": false,
    "ai_gateway_used_for_all_ai_calls": false,
    "evaluation_contract_validated": false,
    "evidence_required": false,
    "critical_error_blocks_pass": false,
    "invalid_ai_json_safe_failure": false,
    "ai_timeout_safe_failure": false,
    "progress_per_trainer_product": false,
    "raw_answers_not_in_analytics": false,
    "ai_cost_logged": false,
    "user_data_isolation_passed": false,
    "admin_routes_protected": false,
    "feature_flag_disable_ai_safe": false,
    "health_ready_checks_pass": false
  },
  "tests": {
    "backend_tests_passed": false,
    "frontend_tests_passed": false,
    "api_tests_passed": false,
    "migration_tests_passed": false,
    "trainer_package_tests_passed": false,
    "ai_gateway_tests_passed": false,
    "evaluation_contract_tests_passed": false,
    "critical_error_tests_passed": false,
    "progress_tests_passed": false,
    "analytics_privacy_tests_passed": false,
    "security_tests_passed": false,
    "localization_tests_passed": false,
    "e2e_smoke_passed": false
  },
  "commands_run": [],
  "artifacts_created": [],
  "known_issues": [],
  "release_gates": {
    "product_scope_gate": "TBD",
    "functional_gate": "TBD",
    "ai_evaluation_gate": "TBD",
    "learning_quality_gate": "TBD",
    "analytics_gate": "TBD",
    "security_privacy_gate": "TBD",
    "localization_gate": "TBD",
    "devops_release_gate": "TBD",
    "qa_gate": "TBD",
    "documentation_gate": "TBD"
  },
  "git": {
    "commit": "",
    "pushed": false,
    "clean": false
  },
  "production": {
    "production_accepted": false,
    "release_allowed": false
  },
  "next_allowed_action": "TBD"
}
```

---

# 13. Definition of Done

This layer is done only if:

```text
all required MVP modules implemented
main user journey works
attempt persists before AI
evaluation works through AI Gateway
result page displays structured evaluation
progress updates
analytics events recorded without raw answers
security ownership tests pass
localization ru/en works
admin seed/status available
feature flag can disable AI safely
health checks work
tests pass
proof JSON completed
known issues documented
git commit/push/clean completed
```

---

# 14. Final Acceptance Verdict Rules

## ACCEPTED

Allowed only if:

```text
all P0 gates pass
no critical/high bugs
proof JSON complete
tests pass
git clean
```

## ACCEPTED_WITH_MINOR_CARRYOVER

Allowed if:

```text
main flow works
no data/security/AI critical issues
only minor UI/documentation polish remains
```

## ACCEPTED_WITH_BLOCKERS

Use if:

```text
useful work completed
but release/development continuation blocked by critical missing piece
```

## REJECTED

Use if:

```text
platform model not preserved
main flow fails
attempts can be lost
AI bypasses gateway
evaluation unreliable
security violation
```

## NEEDS_FIX

Use if:

```text
specific fixable issues remain before acceptance
```

---

# 15. Final Agent Instruction

Implement this as one complete vertical feature-layer.

Do not split into micro-tasks unless internally necessary.  
Do not stop after only backend, only frontend, only docs, or only seed data.  
The task is complete only when the vertical slice works end-to-end and produces artifacts, tests, verification, proof JSON, commit/push/clean git.

---

# 16. Expected Final Report Format

When finished, agent must return:

```markdown
# TRAINER-PLATFORM-MVP-001 — Completion Report

## Verdict
ACCEPTED / ACCEPTED_WITH_BLOCKERS / REJECTED / NEEDS_FIX

## Summary
...

## Implemented
...

## Not Implemented
...

## Forbidden Actions Check
...

## Main User Journey Evidence
...

## Tests
...

## Artifacts
...

## Proof JSON
path: ...

## Git
commit:
pushed:
clean:

## Known Issues
...

## Next Allowed Action
...
```

---

# 17. Final Baseline Lock

```json
{
  "task": "TRAINER-PLATFORM-MVP-001",
  "baseline_locked": true,
  "first_domain": "IT",
  "first_trainer_product": "QA Engineer Interview Trainer",
  "mvp_mode": "text_only",
  "locales": ["ru-RU", "en-US"],
  "architecture": "modular_monolith_first",
  "backend": "FastAPI",
  "frontend": "Next.js + TypeScript",
  "database": "PostgreSQL",
  "ai_gateway_required": true,
  "rubric_based_evaluation_required": true,
  "evidence_required": true,
  "critical_error_pass_forbidden": true,
  "raw_answers_in_analytics_forbidden": true,
  "attempt_loss_forbidden": true,
  "production_accepted": false
}
```
