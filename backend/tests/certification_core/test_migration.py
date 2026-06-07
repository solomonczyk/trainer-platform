"""Tests for migration adapter and database migration."""

from __future__ import annotations

import pytest
import os
import sys
from pathlib import Path


class TestMigrationAdapter:
    """BA/QA migration readiness adapter tests."""

    def test_adapter_importable(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import BaQaMigrationAdapter, MigrationReadinessReport
        assert BaQaMigrationAdapter is not None
        assert MigrationReadinessReport is not None

    def test_migration_readiness_report_structure(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        assert report.ba_mapping_available is True
        assert report.qa_mapping_available is True
        assert report.current_content_unchanged is True
        assert report.migration_dry_run_supported is True
        assert report.migration_executed is False

    def test_report_has_ba_mapping(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        assert hasattr(report, "ba")
        assert hasattr(report.ba, "total_scenarios")
        assert hasattr(report.ba, "activities_count")

    def test_report_has_qa_mapping(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        assert hasattr(report, "qa")
        assert hasattr(report.qa, "total_scenarios")

    def test_report_has_blockers(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        assert hasattr(report, "blockers")
        assert hasattr(report.blockers, "missing_competency_ids")
        assert hasattr(report.blockers, "missing_knowledge_source_refs")
        assert hasattr(report.blockers, "missing_item_lifecycle_state")
        assert hasattr(report.blockers, "missing_rubric_version")

    def test_report_to_dict(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "ba" in d
        assert "qa" in d
        assert "blockers" in d

    def test_report_to_json(self):
        from app.certification_core.migration_adapters.ba_qa_adapter import MigrationReadinessReport
        report = MigrationReadinessReport()
        json_str = report.to_json()
        assert isinstance(json_str, str)
        assert "ba_mapping_available" in json_str

    def test_dry_run_supported(self):
        """Dry run must be supported and not change data."""
        from app.certification_core.migration_adapters.ba_qa_adapter import BaQaMigrationAdapter
        # The adapter class should exist and support dry run
        assert hasattr(BaQaMigrationAdapter, "dry_run_migration")
        assert hasattr(BaQaMigrationAdapter, "generate_report")


class TestDatabaseMigration:
    """Database migration structure tests."""

    def test_migration_file_exists(self):
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        assert migration_file.exists(), f"Migration file not found at {migration_file}"

    def test_migration_has_upgrade_and_downgrade(self):
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert "def upgrade()" in content
        assert "def downgrade()" in content

    def test_migration_revision_correct(self):
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert 'revision = "003"' in content

    def test_migration_no_destructive_changes(self):
        """Migration must not alter BA/QA tables."""
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        # Should reference cert_ tables
        assert "cert_competency_frameworks" in content
        assert "cert_exam_blueprints" in content
        # Should NOT reference existing BA/QA tables
        existing_tables = ["users", "domains", "trainer_products", "scenarios", "activities", "rubrics"]
        for table in existing_tables:
            # Created tables should not be in the upgrade
            assert f'"{table}"' not in content or f'cert_{table}' in content

    def test_migration_rollback_documented(self):
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert "def downgrade()" in content

    def test_foreign_keys_defined(self):
        """Migration should define foreign keys."""
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert "ForeignKey" in content or "sa.ForeignKey" in content

    def test_unique_constraints_defined(self):
        """Migration should define unique constraints for versioning."""
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert "UniqueConstraint" in content
        assert "uq_" in content

    def test_indexes_defined(self):
        """Migration should define indexes for query performance."""
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        assert "create_index" in content

    def test_no_hard_delete_in_migration(self):
        """Certification-grade tables should support soft retirement."""
        migration_dir = Path(__file__).resolve().parent.parent.parent / "app" / "db" / "migrations" / "versions"
        migration_file = migration_dir / "003_certification_grade_core_contracts.py"
        content = migration_file.read_text()
        # All main tables should have valid_until for soft delete
        tables_with_valid_until = content.count("valid_until")
        assert tables_with_valid_until >= 3
