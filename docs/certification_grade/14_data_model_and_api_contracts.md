# Core Data Model and API Contracts

**Document ID:** CGSF-DATA-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Translate the framework into implementable database entities, events and service boundaries.

## Current strategic state
```json
{
  "product_type": "certification_grade_assessment_and_exam_simulation_platform",
  "official_certificate_issuer": false,
  "quality_target": "comparable_to_serious_professional_and_language_exams",
  "current_vertical_slice": "BA Trainer Phase 1 REAL_STAGING_ACCEPTED",
  "production_accepted": false,
  "release_allowed": false
}
```

## Core entities

- `competency_models`, `competencies`, `competency_edges`;
- `exam_blueprints`, `blueprint_nodes`, `blueprint_versions`;
- `knowledge_sources`, `knowledge_snapshots`, `knowledge_changes`;
- `item_specs`, `item_families`, `items`, `item_versions`;
- `item_reviews`, `item_metrics`, `item_exposure`;
- `rubrics`, `rubric_versions`, `anchor_responses`;
- `exam_forms`, `exam_form_items`, `form_equivalence_reports`;
- `exam_sessions`, `session_responses`, `session_events`;
- `evaluations`, `criterion_scores`, `score_reports`;
- `readiness_estimates`, `learning_recommendations`;
- `governance_decisions`, `audit_events`.

## Service boundaries

```text
Knowledge Registry Service
Item Bank Service
Generation & Validation Service
Blueprint Service
Form Assembly Service
Exam Session Service
Scoring Service
AI Evaluation Gateway
Psychometric Service
Adaptive Learning Service
Analytics & Audit Service
```

## Example API contracts

```text
POST /api/v1/item-families
POST /api/v1/items/generate
POST /api/v1/items/{id}/validate
POST /api/v1/items/{id}/approve-pilot
POST /api/v1/items/{id}/calibration
POST /api/v1/exam-forms/assemble
POST /api/v1/exam-sessions
PUT  /api/v1/exam-sessions/{id}/responses/{item_id}
POST /api/v1/exam-sessions/{id}/submit
GET  /api/v1/score-reports/{id}
```

## Cross-cutting contract requirements

- tenant/user authorization;
- optimistic locking/version checks;
- idempotency keys;
- explicit schema versions;
- audit actor and reason;
- no secrets or raw responses in analytics events;
- immutable links to delivered item/rubric/form versions.
