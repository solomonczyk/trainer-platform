# Human Review API Contract

## Routes

| Method | Path | Permission | Description |
|---|---|---|---|
| POST | `/api/v1/certification/review-cases` | `human_review:assign` | Create review case from handoff |
| GET | `/api/v1/certification/review-cases` | `human_review:list` | List/filter review cases |
| GET | `/api/v1/certification/review-cases/{case_id}` | `human_review:read` | Get case detail with candidate/assignments/decisions |
| POST | `/api/v1/certification/review-cases/{case_id}/assign` | `human_review:assign` | Assign reviewer |
| POST | `/api/v1/certification/review-cases/{case_id}/claim` | `human_review:claim` | Claim own assignment |
| POST | `/api/v1/certification/review-cases/{case_id}/release` | `human_review:assign` | Release/remove assignment |
| POST | `/api/v1/certification/review-cases/{case_id}/decision` | `human_review:decide` | Submit review decision |
| GET | `/api/v1/certification/review-cases/{case_id}/history` | `human_review:audit` | Get review audit history |
| GET | `/api/v1/certification/review-cases/{case_id}/evidence` | `human_review:read` | Get evidence snapshot |

## HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created (review case) |
| 400 | Bad request (invalid input, missing fields, state conflict) |
| 403 | Forbidden (role/permission check failed) |
| 404 | Not found |
| 409 | Conflict (duplicate assignment, duplicate decision, stale hash) |

## Request/Response Schemas

### Create Review Case
```
POST /api/v1/certification/review-cases
Request:  { handoff_id: str, review_type?: str }
Response: { case_id, candidate_id, status, ... }
```

### Assign Reviewer
```
POST /api/v1/certification/review-cases/{case_id}/assign
Request:  { reviewer_user_id: str, reviewer_role: str, reason?: str }
Response: { assignment_id, review_case_id, reviewer_user_id, status, message }
```

### Claim
```
POST /api/v1/certification/review-cases/{case_id}/claim
Request:  { reason?: str }
Response: { assignment_id, review_case_id, reviewer_user_id, status, message }
```

### Submit Decision
```
POST /api/v1/certification/review-cases/{case_id}/decision
Request:  {
  decision: "APPROVED_FOR_PILOT_REVIEW"|"REJECTED"|"CHANGES_REQUESTED"|"ESCALATED",
  reason: str,
  findings_json?: dict,
  evidence_confirmed: bool
}
Response: { decision_id, review_case_id, candidate_id, decision, status, message }
```

## Answer-Key Protection

- Review case detail does not expose answer keys or raw provider responses
- The frontend detail page shows candidate content without exposing answer keys directly
- Evidence snapshots reference candidate hash and validation data, not hidden prompts or provider credentials
