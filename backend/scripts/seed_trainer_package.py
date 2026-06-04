#!/usr/bin/env python3
"""Idempotent seed script for trainer packages."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.models import (
    Domain, TrainerProduct, TrainerVersion, TrainerLocalization,
    Scenario, Rubric, RubricCriterion, SkillMap, Skill, CriticalError,
    FeatureFlag, User,
)
from app.core.security import hash_password


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def seed_package(package_dir: Path, db: AsyncSession):
    print(f"Seeding package from: {package_dir}")

    # Load package files
    trainer_data = load_json(package_dir / "trainer.json")
    version_data = load_json(package_dir / "trainer_version.json")
    skill_map_data = load_json(package_dir / "skill_map.json")
    rubric_pack_data = load_json(package_dir / "rubric_pack.json")
    critical_errors_data = load_json(package_dir / "critical_errors.json")

    # 1. Domain
    domain_slug = trainer_data["domain"]
    result = await db.execute(select(Domain).where(Domain.slug == domain_slug))
    domain = result.scalar_one_or_none()
    if not domain:
        domain = Domain(
            slug=domain_slug,
            name=trainer_data.get("domain_name", domain_slug.upper()),
            description=trainer_data.get("domain_description", f"{domain_slug.upper()} domain"),
            is_active=True,
            sort_order=0,
        )
        db.add(domain)
        await db.flush()
        print(f"  Created domain: {domain_slug}")
    else:
        print(f"  Domain exists: {domain_slug}")

    # 2. Trainer Product
    tp_id = trainer_data["trainer_product_id"]
    result = await db.execute(select(TrainerProduct).where(TrainerProduct.trainer_product_id == tp_id))
    trainer = result.scalar_one_or_none()
    if not trainer:
        trainer = TrainerProduct(
            trainer_product_id=tp_id,
            domain_id=domain.id,
            slug=trainer_data["slug"],
            name=trainer_data["name"],
            product_type=trainer_data.get("product_type", "interview_simulator"),
            target_audience=trainer_data.get("target_audience", []),
            default_locale=trainer_data.get("default_locale", "ru-RU"),
            supported_locales=trainer_data.get("supported_locales", ["ru-RU", "en-US"]),
            status=trainer_data.get("status", "published_seed"),
            owner=trainer_data.get("owner", "platform"),
            description=trainer_data.get("description", ""),
            is_published=True,
        )
        db.add(trainer)
        await db.flush()
        print(f"  Created trainer: {tp_id}")
    else:
        print(f"  Trainer exists: {tp_id}")
    tp_db_id = trainer.id

    # 3. Trainer Version
    version_str = version_data["version"]
    result = await db.execute(
        select(TrainerVersion).where(
            TrainerVersion.trainer_product_id == tp_db_id,
            TrainerVersion.version == version_str,
        )
    )
    tver = result.scalar_one_or_none()
    if not tver:
        tver = TrainerVersion(
            trainer_product_id=tp_db_id,
            version=version_str,
            release_status=version_data.get("release_status", "mvp_seed"),
            skill_map_id=version_data.get("skill_map_id"),
            rubric_pack_id=version_data.get("rubric_pack_id"),
            scenario_ids=version_data.get("scenario_ids", []),
            locale_pack_ids=version_data.get("locale_pack_ids", []),
            published_at=datetime.now(timezone.utc),
        )
        db.add(tver)
        await db.flush()
        print(f"  Created version: {version_str}")

    # 4. Skill Map
    sm_id = skill_map_data["skill_map_id"]
    result = await db.execute(select(SkillMap).where(SkillMap.skill_map_id == sm_id))
    sm = result.scalar_one_or_none()
    if not sm:
        sm = SkillMap(skill_map_id=sm_id, skills=skill_map_data.get("skills", []))
        db.add(sm)
        await db.flush()

    # 5. Skills
    for skill in skill_map_data.get("skills", []):
        sid = skill["skill_id"]
        result = await db.execute(select(Skill).where(Skill.skill_id == sid))
        if not result.scalar_one_or_none():
            db.add(Skill(
                skill_id=sid,
                name=skill["name"],
                category=skill.get("category"),
                levels=skill.get("levels"),
                description=skill.get("description", ""),
            ))
    await db.flush()

    # 6. Critical Errors
    for ce in critical_errors_data.get("critical_errors", []):
        ce_id = ce["error_id"]
        result = await db.execute(select(CriticalError).where(CriticalError.error_id == ce_id))
        if not result.scalar_one_or_none():
            db.add(CriticalError(
                error_id=ce_id,
                name=ce.get("name", ce_id),
                description=ce.get("description", ""),
                trainer_product_id=tp_db_id,
                scenario_ids=ce.get("scenario_ids", []),
            ))
    await db.flush()

    # 7. Scenarios + Rubrics
    scenarios_dir = package_dir / "scenarios"
    rubric_ids_to_track = []
    for scenario_file in sorted(scenarios_dir.glob("*.json")):
        scenario_data = load_json(scenario_file)
        sid = scenario_data["scenario_id"]
        result = await db.execute(select(Scenario).where(Scenario.scenario_id == sid))
        existing = result.scalar_one_or_none()
        if not existing:
            scenario = Scenario(
                scenario_id=sid,
                trainer_product_id=tp_db_id,
                title_key=scenario_data.get("title_key", f"scenario.{sid}.title"),
                goal_key=scenario_data.get("goal_key", f"scenario.{sid}.goal"),
                trainer_version=scenario_data.get("trainer_version", "1.0.0"),
                track=scenario_data.get("track", ""),
                module=scenario_data.get("module", ""),
                difficulty=scenario_data.get("difficulty", "junior_basic"),
                estimated_duration_minutes=scenario_data.get("estimated_duration_minutes", 8),
                target_skills=scenario_data.get("target_skills", []),
                user_role=scenario_data.get("user_role", "candidate"),
                ai_role=scenario_data.get("ai_role", "interviewer"),
                rubric_id=scenario_data.get("rubric_id"),
                steps=scenario_data.get("steps", []),
                common_errors=scenario_data.get("common_errors", []),
                critical_errors=scenario_data.get("critical_errors", []),
                hints=scenario_data.get("hints", []),
                status=scenario_data.get("status", "published_seed"),
            )
            db.add(scenario)
            await db.flush()
            print(f"  Created scenario: {sid}")
        else:
            print(f"  Scenario exists: {sid}")

    # 8. Rubrics
    for rubric in rubric_pack_data.get("rubrics", []):
        rid = rubric["rubric_id"]
        result = await db.execute(select(Rubric).where(Rubric.rubric_id == rid))
        existing = result.scalar_one_or_none()
        if not existing:
            rub = Rubric(
                rubric_id=rid,
                pass_score=rubric.get("pass_score", 70),
                critical_fail_enabled=rubric.get("critical_fail_enabled", True),
            )
            db.add(rub)
            await db.flush()
            for crit in rubric.get("criteria", []):
                db.add(RubricCriterion(
                    rubric_id=rub.id,
                    criterion_id=crit["criterion_id"],
                    name=crit.get("name", crit["criterion_id"]),
                    weight=crit.get("weight", 25),
                    evidence_required=crit.get("evidence_required", True),
                ))
            print(f"  Created rubric: {rid}")

    # 9. Locales
    locales_dir = package_dir / "locales"
    for locale_file in locales_dir.glob("*.json"):
        locale_data = load_json(locale_file)
        loc = locale_data.get("locale", locale_file.stem)
        result = await db.execute(
            select(TrainerLocalization).where(
                TrainerLocalization.trainer_product_id == tp_db_id,
                TrainerLocalization.locale == loc,
            )
        )
        if not result.scalar_one_or_none():
            db.add(TrainerLocalization(
                trainer_product_id=tp_db_id,
                locale=loc,
                strings=locale_data.get("strings", {}),
            ))
            print(f"  Created locale: {loc}")

    # 10. Feature flags
    flags = {
        "trainer.qa_interview.visible": True,
        "trainer.qa_interview.enrollment_enabled": True,
        "scenario_runtime.enabled": True,
        "ai_evaluation.enabled": True,
        "ai_evaluation.real_provider_enabled": False,
        "analytics.enabled": True,
        "locale.en_us.enabled": True,
        "beta_access.enabled": False,
    }
    for flag_key, enabled in flags.items():
        result = await db.execute(select(FeatureFlag).where(FeatureFlag.flag_key == flag_key))
        if not result.scalar_one_or_none():
            db.add(FeatureFlag(
                flag_key=flag_key,
                enabled=enabled,
                description=f"Feature flag: {flag_key}",
            ))
    await db.flush()
    print("  Feature flags seeded")

    print("✅ Package seeding complete!")


async def seed_admin_user(db: AsyncSession):
    """Create default admin user if not exists."""
    result = await db.execute(select(User).where(User.email == "admin@trainerplatform.com"))
    if not result.scalar_one_or_none():
        admin = User(
            email="admin@trainerplatform.com",
            password_hash=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.flush()
        print("  Created admin user: admin@trainerplatform.com / admin123")


async def main():
    package_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not package_dir or not package_dir.exists():
        print("Usage: python seed_trainer_package.py <package_dir>")
        print(f"Provided: {package_dir}")
        sys.exit(1)

    # Use sync database URL for seeding (simpler)
    db_url = settings.database_sync_url
    engine = create_async_engine(
        settings.database_url.replace("+asyncpg", ""),
        echo=False,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        try:
            await seed_package(package_dir, db)
            await seed_admin_user(db)
            await db.commit()
            print("\n✅ Seed completed successfully")
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Seed failed: {e}")
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
