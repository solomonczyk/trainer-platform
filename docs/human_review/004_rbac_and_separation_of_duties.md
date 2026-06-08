# RBAC and Separation of Duties — Human Review

## Permissions

| Permission | Description | Assigned To |
|---|---|---|
| `human_review:list` | List review cases | platform_admin, domain_owner, expert_reviewer, psychometric_reviewer, qa_reviewer, generation_operator |
| `human_review:read` | Read case details + evidence | platform_admin, domain_owner, expert_reviewer, psychometric_reviewer, qa_reviewer, generation_operator |
| `human_review:assign` | Assign reviewers to cases | platform_admin, domain_owner |
| `human_review:claim` | Claim own assignment | expert_reviewer, psychometric_reviewer, domain_owner |
| `human_review:decide` | Submit review decision | expert_reviewer, psychometric_reviewer, domain_owner |
| `human_review:escalate` | Escalate a case | platform_admin, domain_owner |
| `human_review:audit` | Read review history | platform_admin, domain_owner, expert_reviewer, psychometric_reviewer, qa_reviewer |

## Separation of Duties — Guards

| Guard | Enforced | Mechanism |
|---|---|---|
| Anonymous review blocked | Yes | Service validates actor_id != "guest" |
| Learner review blocked | Yes | Service rejects "learner"/"registered_user" role |
| Generation operator self-review blocked | Yes | Checks if reviewer == generation request creator |
| Content author self-review blocked | Yes | Role check against SELF_REVIEW_BLOCKED_ROLES |
| LLM / Service account blocked | Yes | Rejects user_id starting with "llm:" or "service:" |
| Wrong role blocked | Yes | Checks against ELIGIBLE_REVIEWER_ROLES |
| Duplicate assignment blocked | Yes | Partial unique index + service check |
| Decision without claim blocked | Yes | Requires CLAIMED assignment status |

## Eligible Reviewer Roles

```python
ELIGIBLE_REVIEWER_ROLES = [
    "expert_reviewer",
    "psychometric_reviewer",
    "domain_owner",
    "qa_reviewer",      # read-only
    "platform_admin",   # assign + decide
]
```

## Prohibited Roles (from reviewing)

```python
PROHIBITED_REVIEWER_ROLES = [
    "generation_operator",
    "content_author",
    "read_only_auditor",
    "learner",
    "guest",
    "llm",
    "service_account",
]
```

## Admin Override Policy

Platform administrators may assign reviewers but cannot bypass separation-of-duties silently. Any admin action requires:
1. Explicit `human_review:assign` permission
2. Reason/correlation ID
3. Audit event record
4. The same self-review and role eligibility checks apply
