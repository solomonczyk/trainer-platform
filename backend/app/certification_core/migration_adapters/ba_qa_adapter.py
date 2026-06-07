"""BA/QA Migration Readiness Adapter.

Maps current BA and QA trainer content into certification-grade contracts
without modifying existing data. Reports readiness level and migration blockers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    TrainerProduct, Scenario, Activity, Rubric, SkillMap, Skill,
)


@dataclass
class MigrationBlockers:
    """Migration blockers identified during readiness assessment."""
    missing_competency_ids: list[str] = field(default_factory=list)
    missing_knowledge_source_refs: list[str] = field(default_factory=list)
    missing_item_lifecycle_state: list[str] = field(default_factory=list)
    missing_rubric_version: list[str] = field(default_factory=list)
    missing_blueprint_mapping: list[str] = field(default_factory=list)


@dataclass
class BaMapping:
    """BA trainer content mapping to certification contracts."""
    total_scenarios: int = 0
    scenarios_with_skills: int = 0
    scenarios_with_rubrics: int = 0
    activities_count: int = 0
    activity_types: list[str] = field(default_factory=list)
    skill_map_count: int = 0
    skills_count: int = 0
    has_competency_mapping: bool = False
    has_knowledge_sources: bool = False
    has_item_lifecycle: bool = False
    has_blueprint: bool = False


@dataclass
class QaMapping:
    """QA trainer content mapping to certification contracts."""
    total_scenarios: int = 0
    scenarios_with_rubrics: int = 0
    activities_count: int = 0
    activity_types: list[str] = field(default_factory=list)
    has_competency_mapping: bool = False
    has_knowledge_sources: bool = False
    has_item_lifecycle: bool = False
    has_blueprint: bool = False


@dataclass
class MigrationReadinessReport:
    """Complete migration readiness report."""
    ba_mapping_available: bool = True
    qa_mapping_available: bool = True
    current_content_unchanged: bool = True
    migration_dry_run_supported: bool = True
    migration_executed: bool = False
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    ba: BaMapping = field(default_factory=BaMapping)
    qa: QaMapping = field(default_factory=QaMapping)
    blockers: MigrationBlockers = field(default_factory=MigrationBlockers)
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class BaQaMigrationAdapter:
    """Read-only adapter that assesses migration readiness for BA and QA trainers.

    Does not modify existing data. Maps current content to certification-grade
    contracts and reports gaps.
    """

    BA_TRAINER_SLUGS = ("interview-simulator-ba", "ba-trainer")
    QA_TRAINER_SLUGS = ("qa-interview", "qa-trainer")

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(self) -> MigrationReadinessReport:
        """Generate a complete migration readiness report."""
        report = MigrationReadinessReport()

        # Map BA trainers
        ba_trainers = await self._get_trainers(self.BA_TRAINER_SLUGS)
        report.ba = await self._map_ba_content(ba_trainers)

        # Map QA trainers
        qa_trainers = await self._get_trainers(self.QA_TRAINER_SLUGS)
        report.qa = await self._map_qa_content(qa_trainers)

        # Identify blockers
        report.blockers = await self._identify_blockers(ba_trainers + qa_trainers)

        # Summary
        report.summary = self._generate_summary(report)

        return report

    async def _get_trainers(self, slugs: tuple[str, ...]) -> list[TrainerProduct]:
        """Get trainer products by slug patterns."""
        results = []
        for slug in slugs:
            result = await self.db.execute(
                select(TrainerProduct).where(TrainerProduct.slug == slug)
            )
            trainer = result.scalar_one_or_none()
            if trainer:
                results.append(trainer)
        return results

    async def _map_ba_content(self, trainers: list[TrainerProduct]) -> BaMapping:
        """Map BA trainer content to certification contracts."""
        mapping = BaMapping()

        for trainer in trainers:
            # Count scenarios
            result = await self.db.execute(
                select(func.count(Scenario.id)).where(
                    Scenario.trainer_product_id == trainer.id
                )
            )
            mapping.total_scenarios += result.scalar() or 0

            # Scenarios with skills
            result = await self.db.execute(
                select(func.count(Scenario.id)).where(
                    Scenario.trainer_product_id == trainer.id,
                    Scenario.target_skills.isnot(None),
                )
            )
            mapping.scenarios_with_skills += result.scalar() or 0

            # Scenarios with rubrics
            result = await self.db.execute(
                select(func.count(Scenario.id)).where(
                    Scenario.trainer_product_id == trainer.id,
                    Scenario.rubric_id.isnot(None),
                )
            )
            mapping.scenarios_with_rubrics += result.scalar() or 0

            # Activities
            result = await self.db.execute(
                select(func.count(Activity.id)).where(
                    Activity.trainer_product_id == trainer.id
                )
            )
            mapping.activities_count += result.scalar() or 0

            # Activity types
            result = await self.db.execute(
                select(Activity.activity_type).where(
                    Activity.trainer_product_id == trainer.id
                ).distinct()
            )
            types = [row[0] for row in result.all() if row[0]]
            mapping.activity_types = list(set(mapping.activity_types + types))

        # Skill maps count
        result = await self.db.execute(select(func.count(SkillMap.id)))
        mapping.skill_map_count = result.scalar() or 0

        # Skills count
        result = await self.db.execute(select(func.count(Skill.id)))
        mapping.skills_count = result.scalar() or 0

        # No competency mapping yet in current BA content
        mapping.has_competency_mapping = False
        mapping.has_knowledge_sources = False
        mapping.has_item_lifecycle = False
        mapping.has_blueprint = False

        return mapping

    async def _map_qa_content(self, trainers: list[TrainerProduct]) -> QaMapping:
        """Map QA trainer content to certification contracts."""
        mapping = QaMapping()

        for trainer in trainers:
            # Count scenarios
            result = await self.db.execute(
                select(func.count(Scenario.id)).where(
                    Scenario.trainer_product_id == trainer.id
                )
            )
            mapping.total_scenarios += result.scalar() or 0

            # Scenarios with rubrics
            result = await self.db.execute(
                select(func.count(Scenario.id)).where(
                    Scenario.trainer_product_id == trainer.id,
                    Scenario.rubric_id.isnot(None),
                )
            )
            mapping.scenarios_with_rubrics += result.scalar() or 0

            # Activities
            result = await self.db.execute(
                select(func.count(Activity.id)).where(
                    Activity.trainer_product_id == trainer.id
                )
            )
            mapping.activities_count += result.scalar() or 0

            # Activity types
            result = await self.db.execute(
                select(Activity.activity_type).where(
                    Activity.trainer_product_id == trainer.id
                ).distinct()
            )
            types = [row[0] for row in result.all() if row[0]]
            mapping.activity_types = list(set(mapping.activity_types + types))

        mapping.has_competency_mapping = False
        mapping.has_knowledge_sources = False
        mapping.has_item_lifecycle = False
        mapping.has_blueprint = False

        return mapping

    async def _identify_blockers(self, trainers: list[TrainerProduct]) -> MigrationBlockers:
        """Identify migration blockers."""
        blockers = MigrationBlockers()

        for trainer in trainers:
            # Missing competency IDs
            result = await self.db.execute(
                select(Scenario.id).where(
                    Scenario.trainer_product_id == trainer.id,
                    Scenario.target_skills.is_(None),
                )
            )
            missing = [str(row[0]) for row in result.all()]
            blockers.missing_competency_ids.extend(missing)

            # Missing knowledge source refs (all current content)
            result = await self.db.execute(
                select(Scenario.id).where(
                    Scenario.trainer_product_id == trainer.id,
                )
            )
            blockers.missing_knowledge_source_refs.extend(
                [str(row[0]) for row in result.all()]
            )

            # Missing item lifecycle state (all current content)
            result = await self.db.execute(
                select(Activity.id).where(
                    Activity.trainer_product_id == trainer.id,
                )
            )
            blockers.missing_item_lifecycle_state.extend(
                [str(row[0]) for row in result.all()]
            )

            # Missing rubric version (scenarios with rubrics but no versioning)
            result = await self.db.execute(
                select(Scenario.id).where(
                    Scenario.trainer_product_id == trainer.id,
                    Scenario.rubric_id.isnot(None),
                )
            )
            blockers.missing_rubric_version.extend(
                [str(row[0]) for row in result.all()]
            )

        return blockers

    def _generate_summary(self, report: MigrationReadinessReport) -> str:
        """Generate a human-readable summary of migration readiness."""
        ba = report.ba
        qa = report.qa
        blockers = report.blockers

        lines = [
            "BA/QA MIGRATION READINESS REPORT",
            "================================",
            f"Generated: {report.generated_at}",
            "",
            "BA Trainer:",
            f"  Scenarios: {ba.total_scenarios}",
            f"  With skills: {ba.scenarios_with_skills}",
            f"  With rubrics: {ba.scenarios_with_rubrics}",
            f"  Activities: {ba.activities_count}",
            f"  Activity types: {ba.activity_types}",
            f"  Skill maps: {ba.skill_map_count}",
            f"  Skills: {ba.skills_count}",
            f"  Has competency mapping: {ba.has_competency_mapping}",
            f"  Has knowledge sources: {ba.has_knowledge_sources}",
            f"  Has item lifecycle: {ba.has_item_lifecycle}",
            "",
            "QA Trainer:",
            f"  Scenarios: {qa.total_scenarios}",
            f"  With rubrics: {qa.scenarios_with_rubrics}",
            f"  Activities: {qa.activities_count}",
            f"  Activity types: {qa.activity_types}",
            "",
            "Migration Blockers:",
            f"  Missing competency IDs: {len(blockers.missing_competency_ids)}",
            f"  Missing knowledge sources: {len(blockers.missing_knowledge_source_refs)}",
            f"  Missing item lifecycle: {len(blockers.missing_item_lifecycle_state)}",
            f"  Missing rubric versions: {len(blockers.missing_rubric_version)}",
            "",
            "Verdict: NOT READY for full migration.",
            "Action required: Map competencies, add knowledge sources, add lifecycle states.",
        ]
        return "\n".join(lines)

    async def dry_run_migration(self) -> dict:
        """Perform a dry-run migration simulation (no data changed)."""
        report = await self.generate_report()
        return {
            "dry_run": True,
            "current_content_unchanged": report.current_content_unchanged,
            "migration_executed": False,
            "readiness": report.to_dict(),
            "recommendations": [
                "Create competency framework for each trainer domain",
                "Register knowledge sources for existing content",
                "Assign item lifecycle states to all activities and scenarios",
                "Create exam blueprints for structured assessment",
                "Upgrade rubrics to versioned format with criteria weights",
            ],
        }
