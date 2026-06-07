# Versioned Entity Immutability Report

**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Task:** FINAL_ENFORCEMENT_AND_POSTGRES_CLOSEOUT  
**Date:** 2026-06-07

## Summary

All versioned entities in the certification‑grade core contracts enforce
immutability for active or published states. Modifications are blocked at the
API layer with HTTP 400 responses, and the system requires creation of new
versions for changes.

## Enforcement Matrix

### Competency Frameworks

| Constraint | Enforcement | Layer |
|---|---|---|
| Active framework update blocked | ✅ HTTP 400 on PATCH | `competency_router.py:109` |
| Active framework delete blocked | ✅ No delete endpoint exists | Router layer |
| Active framework: add competency blocked | ✅ HTTP 400 on POST | `competency_router.py:139` |

When a framework is in `active` status, all PATCH operations (except
status→`deprecated`) are rejected. Adding competencies to an active framework
is also blocked.

### Item Versions

| Constraint | Enforcement | Layer |
|---|---|---|
| Active item version update blocked | ✅ HTTP 400 on PATCH | `item_router.py:107-112` |
| Active item version delete blocked | ✅ No delete endpoint exists | Router layer |
| Published/exam‑eligible item mutation blocked | ✅ HTTP 400 on PATCH | `item_router.py:109` |
| Change requires new version | ✅ `ItemRepository.create_snapshot()` increments version | Repository layer |

Items in status `active`, `published`, `exam_eligible`, `approved_for_pilot`,
or `pilot` cannot be modified. All changes create an immutable version snapshot.

### Rubric Versions

| Constraint | Enforcement | Layer |
|---|---|---|
| Active rubric version update blocked | ✅ HTTP 400 on PATCH | `rubric_router.py:83-88` |
| Active rubric version delete blocked | ✅ No delete endpoint exists | Router layer |
| Change requires new version | ✅ Version field + UniqueConstraint | Model layer |

Rubrics in `active` status are immutable. The `uq_rubric_version` constraint
(`rubric_id`, `version`) enforces uniqueness at the database level.

### Exam Blueprints

| Constraint | Enforcement | Layer |
|---|---|---|
| Published/active blueprint update blocked | ✅ HTTP 400 on PATCH | `blueprint_router.py:105-110` |
| Published/active blueprint delete blocked | ✅ No delete endpoint exists | Router layer |
| Change requires new version/draft copy | ✅ `uq_blueprint_version` constraint | Model layer |

Blueprints in `active` status are fully immutable. Only status transition to
`deprecated` is allowed.

## HTTP Response Codes

All forbidden mutations return:

- **400 Bad Request** — active/published entity modification blocked
- **404 Not Found** — non‑existent entity

No forbidden mutation ever returns 200 or 204.

## Test Coverage

| Test | File | Status |
|---|---|---|
| Cannot modify active framework | `test_acceptance_closeout.py::TestImmutability` | ✅ |
| Cannot modify active item | `test_acceptance_closeout.py::TestEnhancedImmutability` | ✅ |
| Cannot modify active rubric | `test_acceptance_closeout.py::TestEnhancedImmutability` | ✅ |
| Cannot modify published blueprint | `test_acceptance_closeout.py::TestEnhancedImmutability` | ✅ |

## Conclusion

```
{
  "active_framework_update": "blocked",
  "active_framework_delete": "blocked_or_explicitly_disallowed",
  "active_item_version_update": "blocked",
  "active_item_version_delete": "blocked",
  "published_or_exam_eligible_item_mutation": "blocked",
  "change_requires_new_version": true,
  "active_rubric_version_update": "blocked",
  "active_rubric_version_delete": "blocked",
  "published_blueprint_update": "blocked",
  "published_blueprint_delete": "blocked",
  "change_requires_new_version_or_draft_copy": true
}
```
