# Dynamic Item Bank Runtime API Contract

## Base Path

```
/api/v1/certification-core/item-bank/
```

## Endpoints

### Item Authoring

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | /items | Create item draft | certification:write |
| PATCH | /items/{item_id} | Update draft | certification:write |
| POST | /items/{item_id}/submit | Submit for review | certification:write |

### Source Traceability

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | /items/{item_id}/bind-source | Bind knowledge source | certification:write |
| GET | /items/{item_id}/traceability | Get traceability data | certification:read |

### Review

| Method | Path | Description | Auth Required |
|---|---|---|---|
| GET | /reviews/queue | Get review queue | certification:read |
| POST | /items/{item_id}/review | Perform review | certification:item_bank:review |

### Pool Management

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | /items/{item_id}/pilot | Enter pilot pool | certification:manage_lifecycle |
| POST | /items/{item_id}/pilot/complete | Complete pilot | certification:manage_lifecycle |
| POST | /items/{item_id}/exam-eligibility | Grant exam eligibility | certification:manage_lifecycle |
| GET | /pools/pilot | Query pilot pool | certification:read |
| GET | /pools/exam-eligible | Query exam-eligible pool | certification:read |

### Exposure and Rotation

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | /items/{item_id}/exposure | Record exposure | certification:read |
| GET | /items/{item_id}/exposure | Get exposure data | certification:read |
| GET | /items/{item_id}/rotation-eligibility | Check eligibility | certification:read |
| POST | /rotation/policies | Create policy | certification:item_bank:manage |

### Governance

| Method | Path | Description | Auth Required |
|---|---|---|---|
| POST | /items/{item_id}/suspend | Suspend item | certification:item_bank:govern |
| POST | /items/{item_id}/unsuspend | Unsuspend item | certification:item_bank:govern |
| POST | /items/{item_id}/retire | Retire item | certification:item_bank:govern |
| POST | /items/{item_id}/supersede | Supersede item | certification:item_bank:govern |
| GET | /governance/summary | Governance summary | certification:item_bank:audit |
| GET | /governance/incidents | List incidents | certification:item_bank:audit |

## Pagination

All list endpoints support:
- `skip` (int, default 0)
- `limit` (int, default 100, max 500)

## Error Responses

All endpoints return:
- 201 Created — Resource created
- 200 OK — Success
- 400 Bad Request — Validation error
- 403 Forbidden — Insufficient permissions
- 404 Not Found — Resource not found
- 409 Conflict — Resource conflict

## RBAC Summary

| Role | Can Create | Can Review | Can Publish | Can Govern | Can Read Keys |
|---|---|---|---|---|---|
| platform_admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| domain_owner | ✓ | ✓ | ✓ | ✓ | ✓ |
| content_author | ✓ | ✗ | ✗ | ✗ | ✗ |
| expert_reviewer | ✗ | ✓ | ✗ | ✗ | ✗ |
| qa_reviewer | ✗ | ✓ | ✗ | ✗ | ✗ |
| psychometric_reviewer | ✗ | ✓ | ✗ | ✗ | ✗ |
| read_only_auditor | ✗ | ✗ | ✗ | ✗ | ✗ |
| guest | ✗ | ✗ | ✗ | ✗ | ✗ |
