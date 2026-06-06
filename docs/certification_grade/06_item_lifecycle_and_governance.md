# Item Lifecycle and Governance

**Document ID:** CGSF-LIFECYCLE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define item states, transitions, ownership and evidence required from creation through retirement.

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

## Canonical states

```json
[
  "draft",
  "generated",
  "automated_validation_failed",
  "automated_validation_passed",
  "expert_review_required",
  "approved_for_pilot",
  "pilot",
  "calibration_review",
  "calibrated",
  "exam_eligible",
  "under_review",
  "suspended",
  "retired",
  "archived"
]
```

## Transition controls

| Transition | Required authority |
|---|---|
| generated -> automated_validation_passed | validation service |
| automated_validation_passed -> approved_for_pilot | domain expert |
| pilot -> calibrated | psychometric reviewer |
| calibrated -> exam_eligible | assessment owner + domain expert |
| exam_eligible -> suspended | automated risk rule or authorized reviewer |
| suspended -> exam_eligible | full corrective review |
| any active -> retired | content governance decision |

## Suspension triggers

- suspected answer leakage;
- abnormal response statistics;
- multiple credible ambiguity complaints;
- source knowledge changed;
- bias/fairness concern;
- answer key defect;
- excessive exposure;
- legal/copyright issue.

## Audit event

```json
{
  "event_id": "...",
  "item_id": "...",
  "from_status": "exam_eligible",
  "to_status": "suspended",
  "reason_code": "possible_compromise",
  "actor_type": "automated_rule",
  "evidence_refs": ["..."],
  "timestamp": "..."
}
```

## Governance rule

No LLM, author or single engineer may self-approve an item through every stage.
