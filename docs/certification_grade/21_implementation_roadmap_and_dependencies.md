# Implementation Roadmap and Dependencies

**Document ID:** CGSF-ROADMAP-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Sequence development into production-moving vertical layers while avoiding isolated documentation or validator micro-tasks.

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

## Recommended build order

### Layer 1 - Certification-Grade Core Contracts

Deliver:

- competency/blueprint schemas;
- knowledge registry;
- item bank entities and lifecycle;
- governance/audit model;
- API contracts;
- migration adapters.

No exam generation yet.

### Layer 2 - Dynamic Item Factory Vertical Slice

One complete flow:

```text
item specification -> controlled generation -> automated validation
-> expert review queue -> pilot eligibility -> artifacts/tests/browser/admin UI
```

### Layer 3 - Pilot and Psychometric Vertical Slice

Deliver pilot assignment, response metrics, calibration calculations, item health UI and controlled promotion to calibrated state.

### Layer 4 - Exam Form and Session Vertical Slice

Deliver constrained form assembly, exposure controls, strict exam session, scoring and auditable report.

### Layer 5 - Adaptive Practice and Readiness

Deliver mastery estimation, personalized practice and readiness report with uncertainty.

### Layer 6 - First Certification-Grade Domain Pack

Upgrade one domain (recommended software testing foundation or BA foundation) to L3 with expert and pilot evidence.

## Dependency graph

```text
Blueprint + Knowledge Registry
    -> Dynamic Item Bank
        -> Generation/Validation
            -> Pilot/Calibration
                -> Exam Form Assembly
                    -> Exam Session/Scoring
                        -> Readiness/Effectiveness
```

## Phase control

Do not launch many new trainers before core framework and one L3 reference domain pack are proven. Expansion without standards would multiply low-quality static content.

## Current BA Phase 2 note

The previously planned BA Phase 2 must be reconciled with this framework. Scenario functionality can proceed only if its artifacts are created under competency, provenance, rubric and lifecycle contracts rather than as another isolated static bank.
