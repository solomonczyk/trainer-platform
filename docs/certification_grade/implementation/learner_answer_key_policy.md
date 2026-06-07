# Learner Answer-Key Policy

**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Task:** FINAL_ENFORCEMENT_AND_POSTGRES_CLOSEOUT  
**Date:** 2026-06-07

## Role Mapping

The learner role maps to **`authenticated_user_without_certification_admin_role`**.

In the current implementation:

| Token role | Classification | Answer‑key visible? |
|---|---|---|
| `guest` | Learner | No |
| `registered_user` | Learner (not in CERTIFICATION_ROLES) | No |
| `read_only_auditor` | Certification auditor | No |
| `qa_reviewer` | Certification QA | No |
| `content_author` | Certification author | No |
| `expert_reviewer` | Certification reviewer | No |
| `psychometric_reviewer` | Certification reviewer | No |
| `domain_owner` | Certification admin | **Yes** |
| `platform_admin` | Certification admin | **Yes** |

**Key principle:** Any role that does not have `certification:answer_key:read`
permission cannot see answer keys. The `ANSWER_KEY_RESTRICTED_ROLES` set
(`read_only_auditor`, `qa_reviewer`) also explicitly blocks key access.

## Enforcement Points

### 1. Item Detail Endpoint — Role‑Based Filtering

`_filter_item_response()` in `item_router.py` strips `answer_key` from the
response dict for roles that lack `certification:answer_key:read` permission:

```python
def _filter_item_response(item, role: str) -> dict:
    resp = ItemResponse.model_validate(item)
    data = resp.model_dump(mode="json")
    if not AuthorizationService.can_read_answer_keys(role):
        data.pop("answer_key", None)
    return data
```

This is applied to both:
- `GET /api/v1/certification-core/items` (list)
- `GET /api/v1/certification-core/items/{item_id}` (detail)

### 2. Item Create/Update — Input Schemas Only

`ItemCreate` and `ItemUpdate` schemas include `answer_key` as an **input**
field. These endpoints require `certification:write` permission, which is
never granted to learner roles. The OpenAPI schema correctly exposes
`answer_key` only in request bodies, not in response schemas.

### 3. No Answer‑Key Leakage in...

| Context | Status |
|---|---|
| Item list endpoint | ✅ Stripped for learners |
| Item detail endpoint | ✅ Stripped for learners |
| Item version detail | ✅ Version snapshots not exposed via learner API |
| Nested rubric/item response | ✅ No nesting that exposes answer keys |
| Pagination results | ✅ Filtered per‑item |
| Validation errors | ✅ Error responses contain no answer‑key data |
| Audit response | ✅ Audit does not store raw answer keys |
| OpenAPI learner‑facing schemas | ✅ answer_key only in input schemas |

## Test Coverage

| Test | File | Status |
|---|---|---|
| Answer‑key visibility per role | `test_acceptance_closeout.py::TestLearnerAnswerKeyLeakage` | ✅ |
| Answer‑key absent from list for guest | `test_acceptance_closeout.py::TestComprehensiveAnswerKeyLeakage` | ✅ |
| No answer‑key leakage in errors | `test_acceptance_closeout.py::TestComprehensiveAnswerKeyLeakage` | ✅ |
| Learner mapping documented | `test_acceptance_closeout.py::TestComprehensiveAnswerKeyLeakage` | ✅ |
| RBAC: answer_key:read permission | `test_rbac.py::TestLearnerAnswerKeyProtection` | ✅ |

## Conclusion

```
{
  "learner_role_mapping": "authenticated_user_without_certification_admin_role",
  "guest_answer_key_visible": false,
  "learner_answer_key_visible": false,
  "list_endpoint_safe": true,
  "detail_endpoint_safe": true,
  "nested_responses_safe": true,
  "error_responses_safe": true,
  "openapi_schema_safe": true
}
```
