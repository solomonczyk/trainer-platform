"""Executable test for migration 007 full cycle: upgrade → downgrade → upgrade.

Proves the real PostgreSQL migration cycle against the database.
Connects via the ``MIGRATION_DATABASE_URL`` (primary) or
``POSTGRES_MIGRATION_URL`` (fallback) environment variable, or falls
back to ``docker exec`` for local developer environments.

The cycle verified:
    alembic upgrade head  → current=007
    alembic downgrade 006  → current=006
    alembic upgrade head  → current=007
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Connection URL — highest precedence wins
#   1. MIGRATION_DATABASE_URL (primary, used in CI & explicit configs)
#   2. POSTGRES_MIGRATION_URL (legacy fallback)
#   3. None → docker exec trainer-migration-pg (local developer fallback)
# ---------------------------------------------------------------------------
MIGRATION_URL = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("POSTGRES_MIGRATION_URL")
_HAS_PG = MIGRATION_URL is not None

BACKEND = Path(__file__).resolve().parent.parent.parent

MIGRATION_007_TABLES: list[str] = [
    "cert_human_review_cases",
    "cert_reviewer_assignments",
    "cert_human_review_decisions",
]

MIGRATION_006_TABLES: list[str] = [
    "cert_generation_requests",
    "cert_generation_source_bindings",
    "cert_generation_provider_runs",
    "cert_generation_raw_responses",
    "cert_generated_candidates",
    "cert_candidate_validation_runs",
    "cert_candidate_validation_results",
    "cert_candidate_provenance",
    "cert_candidate_review_handoffs",
]


def _to_async_url(url: str) -> str:
    """Convert a sync ``postgresql://`` URL to async ``postgresql+asyncpg://``."""
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _alembic(*args: str) -> str:
    """Run ``alembic <args>`` in the backend directory and return stdout."""
    db_url = _to_async_url(MIGRATION_URL) if _HAS_PG else None
    env = {**os.environ, "DATABASE_URL": db_url} if _HAS_PG else os.environ.copy()
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        pytest.fail(f"alembic {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout + result.stderr


def _pg(sql: str) -> list[tuple | str]:
    """Run SQL against PostgreSQL and return rows.

    Single-column values are returned as strings (for callers that
    compare against plain strings).  Multi-column rows are returned as
    string tuples.
    """
    if MIGRATION_URL:
        try:
            import psycopg2
        except ImportError:
            pytest.fail(
                "psycopg2 is required when using MIGRATION_DATABASE_URL.\n"
                "Install: pip install psycopg2-binary"
            )
        try:
            conn = psycopg2.connect(MIGRATION_URL)
            cur = conn.cursor()
            cur.execute(sql)
            rows: list[tuple | str] = []
            for row in cur.fetchall():
                if len(row) == 1:
                    rows.append(str(row[0]))
                else:
                    rows.append(tuple(str(v) for v in row))
            cur.close()
            conn.close()
            return rows
        except Exception as exc:
            pytest.fail(f"psycopg2 query failed: {exc}")

    cmd = [
        "docker", "exec", "trainer-migration-pg",
        "psql", "-U", "trainer", "-d", "trainer_platform",
        "-t", "-A", "-F", "|",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        pytest.fail(f"docker exec psql failed:\n{result.stderr}")
    rows = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("("):
            continue
        parts = [p.strip() for p in line.split("|")]
        rows.append(tuple(parts) if len(parts) > 1 else parts[0])
    return rows


def _current_revision() -> str:
    """Return the current Alembic revision label."""
    out = _alembic("current")
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith("INFO") and not line.startswith("WARN"):
            return line
    pytest.fail(f"Could not parse alembic current output:\n{out}")


def _tables_exist() -> set[str]:
    """Get all public table names."""
    rows = _pg(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name"
    )
    return {str(r[0]) if isinstance(r, tuple) else str(r) for r in rows}


def _table_has_columns(table: str) -> set[str]:
    """Get column names for a table."""
    rows = _pg(
        "SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = 'public' AND table_name = '{table}'"
    )
    return {str(r[0]) if isinstance(r, tuple) else str(r) for r in rows}


def _table_has_indexes(table: str) -> list[str]:
    """Get index names for a table."""
    rows = _pg(
        "SELECT indexname FROM pg_indexes "
        f"WHERE schemaname = 'public' AND tablename = '{table}' "
        "ORDER BY indexname"
    )
    return [str(r[0]) if isinstance(r, tuple) else str(r) for r in rows]


# ---------------------------------------------------------------------------
# Connection guard
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pg_available():
    """Fail fast if PostgreSQL is not reachable."""
    try:
        result = _pg("SELECT 1 AS ok")
        assert result and result[0] == "1"
    except Exception as exc:
        pytest.fail(f"PostgreSQL unreachable: {exc}")
    return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMigration007Execution:
    """Prove the full migration 007 cycle on real PostgreSQL."""

    def test_cycle_upgrade_downgrade_upgrade(self, pg_available):
        """Full cycle: upgrade head → 007 → downgrade 006 → upgrade head → 007."""
        # Step 1: verify we start at 007
        rev = _current_revision()
        assert rev == "007" or rev.startswith("007"), f"Expected 007, got {rev}"

        # Snapshot 007 tables
        all_tables = _tables_exist()
        for table in MIGRATION_007_TABLES:
            assert table in all_tables, f"Table {table} missing before downgrade"
            cols = _table_has_columns(table)
            assert len(cols) > 2, f"Table {table} has insufficient columns"

        # Count cert_ tables
        cert_tables_before = {t for t in all_tables if t.startswith("cert_")}

        # Step 2: downgrade to 006
        _alembic("downgrade", "006")
        rev = _current_revision()
        assert rev == "006" or rev.startswith("006"), f"Expected 006, got {rev}"

        # Verify 007 tables removed
        tables_after_downgrade = _tables_exist()
        for table in MIGRATION_007_TABLES:
            assert table not in tables_after_downgrade, \
                f"Table {table} still present after downgrade"

        # Verify 006 tables still present
        for table in MIGRATION_006_TABLES:
            assert table in tables_after_downgrade, \
                f"Table {table} missing after downgrade"

        # Step 3: upgrade back to head (007)
        _alembic("upgrade", "007")
        rev = _current_revision()
        assert rev == "007" or rev.startswith("007"), f"Expected 007, got {rev}"

        # Verify 007 tables restored
        tables_after_upgrade = _tables_exist()
        for table in MIGRATION_007_TABLES:
            assert table in tables_after_upgrade, \
                f"Table {table} missing after second upgrade"

        # Verify 006 tables still present
        for table in MIGRATION_006_TABLES:
            assert table in tables_after_upgrade, \
                f"Table {table} missing after second upgrade"

        # Verify no duplicate tables
        cert_tables_after = {t for t in tables_after_upgrade if t.startswith("cert_")}
        assert len(cert_tables_after) == len(cert_tables_before), \
            f"cert_ table count changed: {len(cert_tables_before)} → {len(cert_tables_after)}"

        # Verify alembic version
        rows = _pg("SELECT version_num FROM alembic_version")
        assert len(rows) == 1, f"Expected 1 row in alembic_version, got {len(rows)}"
        assert rows[0] == "007", f"Expected '007', got '{rows[0]}'"

    def test_human_review_tables_schema(self, pg_available):
        """Verify human review table columns and constraints."""
        # cert_human_review_cases columns
        case_cols = _table_has_columns("cert_human_review_cases")
        required_case = {"id", "case_id", "candidate_id", "review_handoff_id",
                         "validation_run_id", "status", "review_type",
                         "required_reviewer_role", "created_by", "version"}
        for col in required_case:
            assert col in case_cols, f"Missing column {col} in cert_human_review_cases"

        # cert_reviewer_assignments columns
        assign_cols = _table_has_columns("cert_reviewer_assignments")
        required_assign = {"id", "assignment_id", "review_case_id", "reviewer_user_id",
                           "reviewer_role", "assigned_by", "status"}
        for col in required_assign:
            assert col in assign_cols, f"Missing column {col} in cert_reviewer_assignments"

        # cert_human_review_decisions columns
        dec_cols = _table_has_columns("cert_human_review_decisions")
        required_dec = {"id", "decision_id", "review_case_id", "assignment_id",
                        "candidate_id", "reviewer_user_id", "decision", "reason",
                        "candidate_hash", "validation_run_id", "created_at"}
        for col in required_dec:
            assert col in dec_cols, f"Missing column {col} in cert_human_review_decisions"

    def test_human_review_table_indexes(self, pg_available):
        """Verify indexes on human review tables."""
        case_indexes = _table_has_indexes("cert_human_review_cases")
        index_names = {idx.split(",")[0] if "," in idx else idx for idx in case_indexes}
        required = {"idx_hrc_status", "idx_hrc_candidate", "idx_hrc_created",
                    "idx_hrc_status_created"}
        for idx in required:
            found = any(idx in i for i in index_names)
            assert found, f"Missing index {idx} on cert_human_review_cases"

        assign_indexes = _table_has_indexes("cert_reviewer_assignments")
        assign_names = {idx.split(",")[0] if "," in idx else idx for idx in assign_indexes}
        required_assign = {"idx_ra_case", "idx_ra_reviewer", "idx_ra_status",
                           "idx_ra_case_status", "idx_ra_one_active_per_case"}
        for idx in required_assign:
            found = any(idx in i for i in assign_names)
            assert found, f"Missing index {idx} on cert_reviewer_assignments"

        dec_indexes = _table_has_indexes("cert_human_review_decisions")
        dec_names = {idx.split(",")[0] if "," in idx else idx for idx in dec_indexes}
        required_dec = {"idx_hrd_case", "idx_hrd_reviewer", "idx_hrd_decision",
                        "idx_hrd_created"}
        for idx in required_dec:
            found = any(idx in i for i in dec_names)
            assert found, f"Missing index {idx} on cert_human_review_decisions"

    def test_existing_certification_tables_preserved(self, pg_available):
        """Existing certification tables must be preserved after the cycle."""
        tables = _tables_exist()
        core_tables = [
            "cert_audit_events", "cert_exam_blueprints", "cert_competency_frameworks",
            "cert_items", "cert_item_versions", "cert_item_families",
            "cert_knowledge_sources", "cert_item_rotation_policies",
            "cert_item_exception_approvals",
        ]
        for table in core_tables:
            assert table in tables, f"Core table {table} missing"

    def test_ba_qa_tables_preserved(self, pg_available):
        """BA/QA tables must be preserved after the cycle."""
        tables = _tables_exist()
        ba_tables = [
            "activities", "deterministic_evaluations", "scenarios",
            "trainer_products", "trainer_progress", "user_trainer_enrollments",
        ]
        for table in ba_tables:
            assert table in tables, f"BA/QA table {table} missing"

    def test_alembic_revision_matches_007(self, pg_available):
        """Final alembic revision must be 007."""
        rev = _current_revision()
        assert rev == "007" or rev.startswith("007"), f"Expected 007, got {rev}"

    def test_database_queryable(self, pg_available):
        """Database must be queryable after the full cycle."""
        rows = _pg("SELECT 1 AS ok")
        assert rows[0] == "1"

    def test_additional_006_tables_preserved(self, pg_available):
        """Additional generation tables must be preserved."""
        tables = _tables_exist()
        gen_tables = [
            "cert_generation_requests",
            "cert_generation_source_bindings",
            "cert_generation_provider_runs",
            "cert_generation_raw_responses",
            "cert_generated_candidates",
            "cert_candidate_validation_runs",
            "cert_candidate_validation_results",
            "cert_candidate_provenance",
            "cert_candidate_review_handoffs",
        ]
        for table in gen_tables:
            assert table in tables, f"Generation table {table} missing"
