# Known Issues — Certification Grade Core Contracts

**Layer:** TRAINER-PLATFORM-CERTIFICATION-GRADE-CORE-CONTRACTS-VERTICAL-LAYER-001  
**Date:** 2026-06-07  

## Open Issues

### 1. SQLite Compatibility for Testing
- **Severity:** Low
- **Description:** The certification models use PostgreSQL features (JSON columns, timezone-aware dates) which work fine in PostgreSQL but are emulated in SQLite test databases. All tests pass, but full migration verification requires PostgreSQL.
- **Workaround:** Tests use SQLite via aiosqlite. Functional behavior is identical.

### 2. Migration Not Executed
- **Severity:** Info
- **Description:** The BA/QA migration adapter is ready but migration has not been executed. Current BA and QA content remains in its original format.
- **Resolution:** Requires separate gate and vertical layer.

### 3. Item Generation Not Implemented
- **Severity:** Info (by design)
- **Description:** Automatic LLM item generation is not included in this layer. The item family template_schema and variant_policy fields are present but generation service is deferred.
- **Resolution:** Planned for next vertical layer (dynamic_item_bank_runtime_and_governance).

### 4. Psychometric Calibration Placeholders
- **Severity:** Info (by design)
- **Description:** `difficulty_measured` and `discrimination_measured` fields exist on items but calibration runtime is not implemented.
- **Resolution:** Requires pilot data collection and calibration service.

### 5. Exam Form Assembly Not Implemented
- **Severity:** Info (by design)
- **Description:** Blueprint section constraints (min/max items, difficulty distributions) are validated but form assembly from the item bank is not implemented.
- **Resolution:** Requires exam form assembly service in a later layer.

### 6. Role-Based Auth is Schema-Level
- **Severity:** Low
- **Description:** RBAC is enforced at the API dependency level. Integration with the application's full user management system is not complete. The certification roles are defined independently.
- **Workaround:** Token-based role extraction works. Full user-role management requires admin UI.

## Resolved Issues

### R1. Class Name Collision (Rubric)
- **Status:** Resolved
- **Fix:** Renamed certification model classes to `CertRubric` and `CertRubricCriterion` to avoid collision with existing `app.db.models.Rubric`.
