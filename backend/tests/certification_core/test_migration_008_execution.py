"""Executable test for migration 008 full cycle: upgrade → downgrade → upgrade.

Proves the real PostgreSQL migration cycle against the database.
Connects via the ``MIGRATION_DATABASE_URL`` (primary) or
``POSTGRES_MIGRATION_URL`` (fallback) environment variable.

The cycle verified:
    alembic upgrade head  → current=008
    alembic downgrade 007  → current=007
    alembic upgrade head   → current=008
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

MIGRATION_URL = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("POSTGRES_MIGRATION_URL")
_HAS_PG = MIGRATION_URL is not None

BACKEND = Path(__file__).resolve().parent.parent.parent

MIGRATION_008_TABLES: list[str] = [
    "quest_sessions",
    "quest_step_results",
]

MIGRATION_007_TABLES: list[str] = [
    "cert_human_review_cases",
    "cert_reviewer_assignments",
    "cert_human_review_decisions",
]


def _psql(sql: str) -> str:
    """Execute a raw SQL statement via psql against the migration database."""
    assert MIGRATION_URL, "MIGRATION_DATABASE_URL must be set"
    parts = MIGRATION_URL.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_port_db = parts[1].split("/")
    host_port = host_port_db[0].split(":")
    dbname = host_port_db[1] if len(host_port_db) > 1 else "trainer_platform"
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"

    env = os.environ.copy()
    env["PGPASSWORD"] = password
    result = subprocess.run(
        ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname, "-t", "-c", sql],
        capture_output=True, text=True, env=env, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")
    return result.stdout


def _current_revision() -> str:
    """Return the current Alembic migration revision."""
    output = _psql("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;")
    return output.strip()


def _tables_exist() -> set[str]:
    """Return set of table names in the public schema."""
    output = _psql(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
    )
    return {t.strip() for t in output.splitlines() if t.strip()}


def _table_has_columns(table_name: str) -> list[str]:
    """Return column names for a given table."""
    output = _psql(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = 'public' AND table_name = '{table_name}' "
        f"ORDER BY ordinal_position;"
    )
    return [c.strip() for c in output.splitlines() if c.strip()]


def _alembic(cmd: str, arg: str) -> None:
    """Run an Alembic command (e.g., ``upgrade head``, ``downgrade 007``)."""
    # Use the PostgreSQL migration URL to keep alembic and psql queries in sync
    db_url = MIGRATION_URL.replace("postgresql://", "postgresql+asyncpg://") if MIGRATION_URL else os.environ.get("DATABASE_URL", "")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", cmd, arg],
        capture_output=True, text=True, timeout=120,
        cwd=str(BACKEND),
        env={**os.environ, "DATABASE_URL": db_url, "APP_ENV": "testing"},
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"alembic {cmd} {arg} failed")


pytestmark = [
    pytest.mark.skipif(not _HAS_PG, reason="MIGRATION_DATABASE_URL not set"),
]


class TestMigration008Cycle:
    """Full migration 008 lifecycle test against real PostgreSQL."""

    def test_cycle_upgrade_downgrade_upgrade(self):
        """Full cycle: upgrade head -> 008 -> downgrade 007 -> upgrade head -> 008."""
        # Step 1: verify we start at 008
        rev = _current_revision()
        assert rev == "008" or rev.startswith("008"), f"Expected 008, got {rev}"

        # Snapshot 008 tables
        all_tables = _tables_exist()
        for table in MIGRATION_008_TABLES:
            assert table in all_tables, f"Table {table} missing before downgrade"
            cols = _table_has_columns(table)
            assert len(cols) > 2, f"Table {table} has insufficient columns"

        # Count quest_ tables
        quest_tables_before = {t for t in all_tables if t.startswith("quest_")}

        # Verify 007 tables are still present
        for table in MIGRATION_007_TABLES:
            assert table in all_tables, f"Table {table} missing before downgrade"

        # Step 2: downgrade to 007
        _alembic("downgrade", "007")
        rev = _current_revision()
        assert rev == "007" or rev.startswith("007"), f"Expected 007, got {rev}"

        # Verify 008 tables removed
        tables_after_downgrade = _tables_exist()
        for table in MIGRATION_008_TABLES:
            assert table not in tables_after_downgrade, \
                f"Table {table} still present after downgrade"

        # Verify 007 tables still present
        for table in MIGRATION_007_TABLES:
            assert table in tables_after_downgrade, \
                f"Table {table} missing after downgrade"

        # Step 3: upgrade back to head (008)
        _alembic("upgrade", "head")
        rev = _current_revision()
        assert rev == "008" or rev.startswith("008"), f"Expected 008, got {rev}"

        # Verify 008 tables restored
        tables_after_upgrade = _tables_exist()
        for table in MIGRATION_008_TABLES:
            assert table in tables_after_upgrade, \
                f"Table {table} missing after second upgrade"

        # Verify 007 tables still present
        for table in MIGRATION_007_TABLES:
            assert table in tables_after_upgrade, \
                f"Table {table} missing after second upgrade"
