# Dynamic Item Bank Runtime — PostgreSQL Migration Report

## Overview

Migration `004` adds 10 runtime tables to support the operational Dynamic Item Bank.

## Migration Details

| Field | Value |
|---|---|
| Revision | 004 |
| Down Revision | 003 |
| Date | 2026-06-07 |
| PostgreSQL | 16 (Debian) |
| Tables Added | 10 |
| BA/QA Tables Preserved | 28 |
| Core Cert Tables Preserved | 12 |

## Migration Cycle

| Step | Result |
|---|---|
| Upgrade to 004 | PASSED |
| Downgrade to 003 | PASSED |
| Second Upgrade to 004 | PASSED |

## Tables Created

1. `cert_item_source_bindings` — Traceability snapshots
2. `cert_item_reviews` — Review records
3. `cert_item_review_decisions` — Immutable decision trail
4. `cert_item_pool_memberships` — Pilot and exam-eligible pools
5. `cert_item_exposure_events` — Idempotent exposure log
6. `cert_item_exposure_counters` — Aggregated counters
7. `cert_item_rotation_policies` — Rotation configuration
8. `cert_item_governance_incidents` — Governance flags
9. `cert_item_supersession_links` — Supersession tracking
10. `cert_item_exception_approvals` — Controlled exceptions

## Schema Verification

| Check | Status |
|---|---|
| 13 foreign keys | ✓ Verified |
| 4 unique constraints | ✓ Verified |
| 24 indexes | ✓ Verified |
| BA/QA tables preserved | ✓ 28 tables intact |
| Core cert tables preserved | ✓ 12 tables intact |
