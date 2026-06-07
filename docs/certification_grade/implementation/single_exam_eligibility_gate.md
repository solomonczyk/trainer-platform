# Single Exam-Eligibility Gate

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002
**Date:** 2026-06-07

## Authoritative Entry Point

All transitions to `exam_eligible` MUST pass through:

```python
ExamEligibilityGateService.evaluate_and_grant_exam_eligibility(...)
```

## Blocked Paths

| Path | Status |
|------|--------|
| Direct ORM status mutation | ✅ No pool membership without gate |
| Repository `update_status` | ✅ Not exposed externally |
| Generic item update endpoint | ✅ Blocked — non-draft items not editable |
| Authoring service shortcut | ✅ Blocked — status check prevents |
| Pilot service shortcut | ✅ Deprecated — router delegates to gate |
| Lifecycle transition bypass | ✅ Gate is the single policy enforcement point |

## Gate Validation Checks

1. Item exists check
2. Suspended/retired check (cannot grant eligibility)
3. Controlled exception validation (if provided)
4. Calibrated status check (standard path)
5. Source traceability validation
6. Active rubric check
7. Duplicate pool membership check
8. Pool membership creation
9. Status transition to `exam_eligible`
10. Version snapshot
11. Audit event: `exam_eligibility_granted` / `exam_eligibility_denied`

## Test Results

- ✅ 3 positive tests (gate grants eligibility)
- ✅ 9 negative tests (bypasses blocked, validation failures rejected)
- All 12 tests pass
