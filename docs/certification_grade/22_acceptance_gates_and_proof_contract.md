# Acceptance Gates and Proof Contract

**Document ID:** CGSF-ACCEPTANCE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define the mandatory Definition of Done, evidence artifacts and proof JSON for future implementation tasks.

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

## Global Definition of Done

A full vertical layer is complete only when it includes:

- implementation;
- database migrations/contracts;
- runtime and UI;
- security and privacy controls;
- tests;
- real browser acceptance where user-facing;
- operator visual review;
- documentation and artifacts;
- proof JSON;
- commit, push and clean git.

## Hard gates

```json
{
  "generation_gate": "separate_authorization_or_approved_pipeline",
  "expert_review_gate": "required_before_pilot",
  "pilot_gate": "required_before_calibrated",
  "calibration_gate": "required_before_exam_eligible",
  "exam_assembly_gate": "only_exam_eligible_items",
  "release_gate": "quality_security_browser_and_evidence_pass",
  "production_accepted_true": "separate_operator_decision"
}
```

## Minimum proof JSON

```json
{
  "layer": "",
  "verdict": "TBD",
  "goal": "",
  "allowed_scope_respected": false,
  "forbidden_actions_absent": false,
  "implementation": {},
  "data_migrations": {},
  "tests": {},
  "browser_acceptance": {},
  "visual_review": {},
  "security_privacy": {},
  "artifacts": [],
  "git": {"commit": "", "pushed": false, "clean": false},
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": ""
}
```

## Certification-grade domain release gates

- approved competency model and blueprint;
- active trusted source registry;
- required item-bank volume and diversity;
- item provenance completeness;
- expert review and pilot evidence;
- psychometric reliability target met;
- equivalent exam forms verified;
- scoring/pass policy approved;
- AI/human calibration passed for open responses;
- exposure and compromise controls active;
- accessibility, bias, privacy and security reviews passed;
- real browser acceptance passed;
- effectiveness claims limited to available evidence.

## Forbidden acceptance shortcuts

- accepting author-labelled difficulty as calibration;
- accepting a real AI response with `validation_status=partial`;
- accepting API-only tests for a browser workflow;
- marking an item exam-eligible directly after generation;
- using static questions indefinitely without rotation/exposure controls;
- claiming serious exam readiness without uncertainty and evidence;
- claiming `production_accepted=true` inside an implementation task.
