## Migration 006 Execution Report

### Cycle

005 → 006 (upgrade)
006 → 005 (downgrade)
005 → 006 (second upgrade)

### Results

| Step | Status | Revision |
|------|--------|----------|
| Initial upgrade | PASSED | 006 |
| Downgrade | PASSED | 005 |
| Second upgrade | PASSED | 006 |

### Tables Created

1. cert_generation_requests
2. cert_generation_source_bindings
3. cert_generation_provider_runs
4. cert_generation_raw_responses
5. cert_generated_candidates
6. cert_candidate_validation_runs
7. cert_candidate_validation_results
8. cert_candidate_provenance
9. cert_candidate_review_handoffs

### Constraints

- cert_generation_requests.correlation_id UNIQUE
- cert_candidate_provenance.candidate_id UNIQUE
- cert_candidate_validation_runs.candidate_id UNIQUE (one run per candidate)
- cert_candidate_review_handoffs.candidate_id UNIQUE (one handoff per candidate)

### Indexes (partial list)

- ix_cert_generation_requests_status
- ix_cert_generation_provider_runs_status
- ix_cert_generation_source_bindings_request_id
- ix_cert_generated_candidates_request_id
- ix_cert_candidate_validation_runs_decision
- ix_cert_candidate_provenance_provider

### Migration 005 Cycle Verification

Both migration 005 and 006 tests pass independently and together (10 tests total):

| Test | Result |
|------|--------|
| 005: upgrade → downgrade 004 → upgrade head | PASSED |
| 005: tables preserved after cycle (60 total) | PASSED |
| 005: cert_ table count (31) | PASSED |
| 005: alembic revision matches head (006) | PASSED |
| 005: database queryable | PASSED |
| 006: upgrade → downgrade 005 → upgrade head | PASSED |
| 006: cert_ tables preserved | PASSED |
| 006: BA/QA tables preserved | PASSED |
| 006: alembic revision matches 006 | PASSED |
| 006: database queryable | PASSED |

All 5 pre-existing migration 005 errors resolved (container reference fix, database name fix, head revision alignment).

### PostgreSQL Details

- Container: `trainer-migration-pg`
- Database: `trainer_platform`
- Connection: docker exec psql or POSTGRES_MIGRATION_URL
- Total tables: 60 (31 cert_ + 29 non-cert)
- Current revision: 006
