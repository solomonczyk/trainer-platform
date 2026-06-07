# PostgreSQL Migration Cycle Report

**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Task:** FINAL_ENFORCEMENT_AND_POSTGRES_CLOSEOUT  
**Date:** 2026-06-07

## Summary

Real PostgreSQL 16.14 was provisioned via Docker on a dedicated instance. The
full upgrade → downgrade → upgrade migration cycle was executed and verified
against live PostgreSQL.

## Environment

| Item | Value |
|---|---|
| PostgreSQL version | 16.14 (Debian 16.14-1.pgdg13+1) |
| Host | localhost:55432 (Docker container) |
| Database | `trainer_cert_core` |
| Alembic revisions | 001, 002, 003 |

## Migration Fixes Applied During Execution

Two bugs were discovered and fixed in migration `003_certification_grade_core_contracts.py`:

1. **Wrong `down_revision` value**: The migration specified
   `down_revision = "002_ba_trainer_activities"` but the actual revision ID in
   version `002` is `"002"`. Fixed to `down_revision = "002"`.

2. **Constraint name collision with BA schema**: The `cert_rubric_criteria`
   table used the unique‑constraint name `uq_rubric_criterion`, which is
   already used by the BA `rubric_criteria` table (PostgreSQL requires
   schema‑unique constraint names). Renamed to `uq_cert_rubric_criterion`.

## Cycle Results

### Phase 1: Upgrade to Head

```
alembic upgrade head  →  PASSED
```

Revisions applied in order:
- `None` → `001` (Initial MVP schema)
- `001` → `002` (BA Trainer deterministic activities)
- `002` → `003` (Certification‑grade core contracts)

### Phase 2: Verify Tables at Head (003)

| Check | Result |
|---|---|
| Total tables after upgrade | 41 |
| `cert_` tables created | **12** |
| BA/QA tables preserved | **29** (all present) |
| Foreign keys on cert tables | Verified (see below) |
| Unique/version constraints | Verified (see below) |
| Indexes | Verified (see below) |

**12 cert tables created:**

```
cert_competency_frameworks    cert_competencies
cert_exam_blueprints          cert_blueprint_sections
cert_knowledge_sources        cert_item_families
cert_items                    cert_item_versions
cert_rubrics                  cert_rubric_criteria
cert_domain_packs             cert_audit_events
```

**Foreign keys verified:**

- `cert_competencies.framework_id` → `cert_competency_frameworks.id`
- `cert_competencies.parent_id` → `cert_competencies.id`
- `cert_blueprint_sections.blueprint_id` → `cert_exam_blueprints.id`
- `cert_item_versions.item_id` → `cert_items.id`
- `cert_items.item_family_id` → `cert_item_families.id`
- `cert_rubric_criteria.rubric_id` → `cert_rubrics.id`

**Unique/version constraints verified:**

- `uq_competency_framework_version`, `uq_competency_per_framework`
- `uq_blueprint_version`, `uq_blueprint_section`
- `uq_knowledge_source_version`
- `uq_item_version`
- `uq_rubric_version`, `uq_cert_rubric_criterion`
- `uq_domain_pack_version`

**Indexes verified:**

24 cert‑specific indexes created covering entity_type, status, domain_pack,
actor, and timestamp queries.

### Phase 3: Downgrade to 002

```
alembic downgrade 002  →  PASSED
```

After downgrade:
- `cert_` tables count: **0** (all 12 dropped)
- BA/QA tables preserved: **29** (no change)
- `alembic_version` at revision: `002`

### Phase 4: Second Upgrade to Head

```
alembic upgrade head  →  PASSED
```

After upgrade:
- `cert_` tables count: **12** (all recreated)
- `alembic current`: `003` (head)
- BA/QA tables still intact: **29**

## Conclusion

```
{
  "postgres_instance_started": true,
  "upgrade_to_head_passed": true,
  "cert_tables_created": 12,
  "constraints_verified": true,
  "indexes_verified": true,
  "ba_qa_tables_preserved": true,
  "downgrade_to_002_passed": true,
  "cert_tables_removed_after_downgrade": true,
  "second_upgrade_to_head_passed": true,
  "alembic_current_is_003": true
}
```
