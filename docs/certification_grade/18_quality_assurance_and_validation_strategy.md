# Quality Assurance and Validation Strategy

**Document ID:** CGSF-QA-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define tests and acceptance evidence for platform runtime, assessment content, psychometrics, AI evaluation and real browser behavior.

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

## Test layers

### Unit and contract tests

- schema and state transitions;
- scoring formulas;
- blueprint validators;
- exposure rules;
- idempotency and authorization;
- analytics privacy filters.

### Content validation

- answer-key correctness;
- ambiguity and duplicate checks;
- source provenance;
- rubric consistency;
- locale review.

### Integration tests

- item generation to review queue;
- form assembly to session delivery;
- session submission to scoring;
- AI evaluation to progress;
- source update to affected-item flags.

### E2E/browser acceptance

- learning, practice and exam modes;
- timers and recovery;
- refresh/relogin persistence;
- user isolation;
- no localhost/critical errors;
- visible, readable and usable result reports.

### Statistical validation

- item metrics;
- reliability;
- form equivalence;
- evaluator agreement;
- readiness calibration.

## Required visual review

Technical success cannot override broken presentation. Operator visual review is mandatory for exam instructions, item rendering, timers, answer controls, feedback and score reports.

## Acceptance verdicts

- `ACCEPTED`: all hard gates and evidence pass.
- `ACCEPTED_WITH_BLOCKERS`: implementation exists but high-impact evidence is incomplete.
- `REJECTED`: security, isolation, scoring integrity or fabricated evidence failure.
- `NEEDS_OPERATOR_ACTION`: explicit external/manual gate required.

## Regression baseline

Every new domain pack must preserve existing accepted BA Trainer and QA Trainer vertical slices until a planned migration supersedes them.
