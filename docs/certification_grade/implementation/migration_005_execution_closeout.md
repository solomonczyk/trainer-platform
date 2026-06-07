# Migration 005 Execution Closeout

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002
**Closeout:** MIGRATION_005_EXECUTION_CLOSEOUT_002B
**Date:** 2026-06-07
**Task Agent:** Backend / Database Migration / Regression / Acceptance Engineering

---

## Migration 005 Summary

| Field | Value |
|---|---|
| Revision | 005 |
| Down Revision | 004 |
| PostgreSQL | 16.14 (Debian, Docker container) |
| Temporary Database | `trainer_item_bank_closeout` |
| Credentials Committed | No |

## Tables Modified by 005

### `cert_item_rotation_policies` — 7 new columns

| Column | Type | Nullable | Default |
|---|---|---|---|
| `allowed_locales` | JSON | YES | — |
| `domain_balance_quotas` | JSON | YES | — |
| `competency_balance_quotas` | JSON | YES | — |
| `difficulty_balance_ratios` | JSON | YES | — |
| `max_items_per_family` | Integer | NO | 3 |
| `recent_use_window_days` | Integer | NO | 90 |
| `exposure_threshold` | Integer | NO | 50 |

### `cert_item_exception_approvals` — 9 new columns + 3 indexes

| Column | Type | Nullable | Default |
|---|---|---|---|
| `item_version_id` | String(100) | YES | — |
| `scope` | String(100) | YES | — |
| `requested_by` | String(100) | YES | — |
| `requester_role` | String(50) | YES | — |
| `first_approver` | String(100) | YES | — |
| `first_approval_timestamp` | DateTime(tz) | YES | — |
| `second_approval_timestamp` | DateTime(tz) | YES | — |
| `status` | String(20) | NO | `'pending'` |
| `audit_correlation_id` | String(100) | YES | — |

**Indexes created:** `idx_iea_status`, `ix_cert_item_exception_approvals_item_version_id`, `ix_cert_item_exception_approvals_status`

## Migration Cycle Results

| Step | Command | Result |
|---|---|---|
| Initial Upgrade 004 → 005 | `alembic upgrade head` | PASSED |
| Current Revision | `alembic current` | `005` |
| Downgrade 005 → 004 | `alembic downgrade 004` | PASSED |
| Current Revision | `alembic current` | `004` |
| Second Upgrade 004 → 005 | `alembic upgrade head` | PASSED |
| Current Revision | `alembic current` | `005` |

## Schema Verification

| Check | Result |
|---|---|
| 005 columns present before downgrade | 16/16 |
| 005 columns removed after downgrade | 16/16 |
| 005 indexes removed after downgrade | 3/3 |
| 005 columns restored after second upgrade | 16/16 |
| 005 indexes restored after second upgrade | 3/3 |
| Certification tables preserved | 22/22 |
| BA/QA tables preserved | 8/8 |
| Total tables | 51 |
| Duplicate objects | None |
| Database queryable | Yes |

## Migration Test

```bash
python -m pytest tests/certification_core/test_migration_005_execution.py -v
```

**Passed:** 5 / **Failed:** 0 / **Skipped:** 0

Tests proved:
1. Full upgrade → downgrade → upgrade cycle
2. All 51 tables preserved after cycle
3. 22 cert_ tables exist
4. Final revision is 005
5. Database queryable

## Integrity Verification (PostgreSQL metadata queries)

| Check | Value |
|---|---|
| Tables verified | 51 |
| Columns verified | 16 005 columns |
| Foreign keys | 47 |
| Unique constraints | 33 |
| Indexes verified | 3 005 indexes |
| Alembic revision | 005 |

## No Destructive Changes

- No BA/QA tables were modified
- All 22 certification tables remain intact
- All 8 BA/QA tables remain intact
- No data loss occurred
