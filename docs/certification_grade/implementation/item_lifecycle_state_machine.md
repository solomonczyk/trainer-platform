# Item Lifecycle State Machine

**Document ID:** CGSF-IMPL-LIFECYCLE-001  
**Date:** 2026-06-07  

## Canonical States (14 states)

```
draft → generated → automated_validation_failed → automated_validation_passed
                                                       ↓
                                              expert_review_required
                                                       ↓
                                                approved_for_pilot
                                                       ↓
                                                     pilot
                                                       ↓
                                             calibration_review
                                                       ↓
                                                  calibrated
                                                       ↓
                                              exam_eligible
                                                       ↓
                                              under_review → suspended
                                                       ↓
                                                    retired → archived
```

## Key Allowed Transitions

| From | To | Required Role |
|------|----|---------------|
| draft | generated | content_author |
| draft | expert_review_required | content_author |
| generated | automated_validation_passed | (automated) |
| automated_validation_passed | expert_review_required | content_author |
| expert_review_required | approved_for_pilot | expert_reviewer |
| approved_for_pilot | pilot | domain_owner |
| pilot | calibration_review | psychometric_reviewer |
| calibration_review | calibrated | psychometric_reviewer |
| calibrated | exam_eligible | domain_owner |
| exam_eligible | suspended | expert_reviewer |
| suspended | under_review | domain_owner |
| * | retired | domain_owner |
| retired | archived | (automated) |

## Forbidden Transitions (documented and enforced)

| From | To | Reason |
|------|----|--------|
| draft | exam_eligible | Direct bypass of all validation gates |
| generated | exam_eligible | Items must pass validation, review, pilot, calibration |
| generated | approved_for_pilot | Items must pass automated validation first |
| draft | approved_for_pilot | Items must undergo validation and review |
| approved_for_pilot | exam_eligible | Items must complete pilot and calibration |
| pilot | exam_eligible | Items must complete calibration first |
| suspended | exam_eligible | Requires full corrective review |
| retired | exam_eligible | Terminal state |
| retired | pilot | Terminal state |

## LLM Self-Approval Prevention

- Actors with `actor_id` starting with `llm:` cannot perform expert_reviewer or domain_owner gated transitions
- Content authors cannot self-approve expert review
- Domain owners cannot self-approve calibration gates

## Role Gates

```python
ROLE_GATES = {
    ("automated_validation_passed", "expert_review_required"): "content_author",
    ("expert_review_required", "approved_for_pilot"): "expert_reviewer",
    ("approved_for_pilot", "pilot"): "domain_owner",
    ("pilot", "calibration_review"): "psychometric_reviewer",
    ("calibration_review", "calibrated"): "psychometric_reviewer",
    ("calibrated", "exam_eligible"): "domain_owner",
    ("exam_eligible", "suspended"): "expert_reviewer",
    ("suspended", "under_review"): "domain_owner",
    ("suspended", "draft"): "domain_owner",
    ("*", "retired"): "domain_owner",
}
```
