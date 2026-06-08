# Human Review State Machine

## States

```
PENDING_ASSIGNMENT → ASSIGNED → IN_REVIEW → {APPROVED_FOR_PILOT_REVIEW, REJECTED, CHANGES_REQUESTED, ESCALATED} → CLOSED
```

## Transitions

| From | To | Required Action | Actor |
|---|---|---|---|
| PENDING_ASSIGNMENT | ASSIGNED | Reviewer assigned | Admin/Domain Owner |
| PENDING_ASSIGNMENT | CLOSED | Case closed | Admin |
| ASSIGNED | IN_REVIEW | Reviewer claims assignment | Reviewer |
| ASSIGNED | CLOSED | Case closed | Admin |
| ASSIGNED | PENDING_ASSIGNMENT | Assignment released | Admin |
| IN_REVIEW | APPROVED_FOR_PILOT_REVIEW | Decision submitted | Reviewer |
| IN_REVIEW | REJECTED | Decision submitted | Reviewer |
| IN_REVIEW | CHANGES_REQUESTED | Decision submitted | Reviewer |
| IN_REVIEW | ESCALATED | Decision submitted | Reviewer |
| IN_REVIEW | CLOSED | Case closed | Admin |
| _terminal_ | CLOSED | Case closed | Admin |

## Forbidden Transitions

- All direct transitions to `pilot`, `exam_eligible`, or `published` pools
- Direct `PENDING_ASSIGNMENT` → `APPROVED_FOR_PILOT_REVIEW` (bypasses review)
- Decision after case is `CLOSED`
- Reopening a completed case
