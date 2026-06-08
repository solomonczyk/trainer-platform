# Migration 007 — Evidence

## Revision

- **ID**: `007`
- **Down Revision**: `006` (controlled item generation)
- **Created**: 2026-06-08
- **Type**: Schema addition (non-destructive)

## Tables Created

| Table | Purpose |
|---|---|
| `cert_human_review_cases` | Persistent review case records |
| `cert_reviewer_assignments` | Reviewer assignment tracking |
| `cert_human_review_decisions` | Append-only immutable decision records |

## Key Constraints

1. Partial unique index `idx_ra_one_active_per_case` on `cert_reviewer_assignments(review_case_id) WHERE status IN ('ASSIGNED', 'CLAIMED')`
2. Foreign keys: cases → candidates, handoffs, validation runs; assignments → cases; decisions → cases, assignments, candidates, validation runs
3. Decision values constrained to `APRROVED_FOR_PILOT_REVIEW`, `REJECTED`, `CHANGES_REQUESTED`, `ESCALATED`
4. No hard-delete on any table

## Upgrade Cycle

```
006 → 007: CREATE 3 tables + 13 indexes
007 → 006: DROP 3 tables + 13 indexes
006 → 007: RE-CREATE 3 tables + 13 indexes
```

## Data Preservation

All existing tables from migrations 001–006 are preserved without modification.
