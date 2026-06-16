"""Seed/load BA trainer package data into the database."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Domain, TrainerProduct, TrainerVersion, TrainerLocalization,
    Track, Module, Activity,
)

PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "trainer_packages" / "business_analyst_interview_trainer"


async def seed_ba_trainer(db: AsyncSession, inline: object = None) -> dict:
    """Load the BA trainer package from JSON files or inline data into the database.

    Args:
        db: Database session.
        inline: Optional ``InlineSeedRequest`` with ``trainer_data``, ``modules_data``,
            ``activities_data``, and ``locale_data``. When provided, these override
            file-based loading — useful in environments like Railway Docker where
            ``trainer_packages/`` is not deployed.

    Returns:
        A dict with counts of created records, or an error dict.
    """
    results = {"domain": 0, "trainer": 0, "version": 0, "localization": 0, "track": 0, "module": 0, "activities": 0}

    # 1. Load package files (or use inline data)
    if inline and getattr(inline, "trainer_data", None):
        trainer_manifest = inline.trainer_data
    else:
        trainer_manifest = _load_json("trainer.json")

    if inline and getattr(inline, "modules_data", None):
        modules_data = inline.modules_data
    else:
        modules_data = _load_json("modules.json")

    if inline and getattr(inline, "activities_data", None):
        activities_data = inline.activities_data
    else:
        activities_data = _load_json("activities.json")

    if inline and getattr(inline, "locale_data", None):
        locale_data = inline.locale_data
    else:
        locale_data = _load_json("locales/ru-RU.json")

    if not all([trainer_manifest, modules_data, activities_data, locale_data]):
        return {"error": "Failed to load one or more package files"}

    # 2. Ensure IT domain exists
    result = await db.execute(select(Domain).where(Domain.slug == trainer_manifest.get("domain", "it")))
    domain = result.scalar_one_or_none()
    if not domain:
        domain = Domain(
            slug=trainer_manifest.get("domain", "it"),
            name="IT",
            description="Information Technology",
            is_active=True,
            sort_order=0,
        )
        db.add(domain)
        await db.flush()
        results["domain"] = 1

    # 3. Create TrainerProduct
    tp_id = trainer_manifest["trainer_product_id"]
    result = await db.execute(select(TrainerProduct).where(TrainerProduct.trainer_product_id == tp_id))
    trainer = result.scalar_one_or_none()
    if not trainer:
        trainer = TrainerProduct(
            trainer_product_id=tp_id,
            domain_id=domain.id,
            slug=trainer_manifest["slug"],
            name=trainer_manifest["name"],
            product_type=trainer_manifest.get("product_type", "interview_simulator"),
            target_audience=trainer_manifest.get("target_audience", []),
            default_locale=trainer_manifest.get("default_locale", "ru-RU"),
            supported_locales=trainer_manifest.get("supported_locales", ["ru-RU"]),
            status=trainer_manifest.get("status", "staging"),
            owner=trainer_manifest.get("owner", "platform"),
            description=trainer_manifest.get("description", ""),
            is_published=True,
        )
        db.add(trainer)
        await db.flush()
        results["trainer"] = 1

    # 4. Create/update TrainerVersion
    version_id = trainer.id
    version_str = trainer_manifest.get("version", "0.1.0")
    result = await db.execute(
        select(TrainerVersion).where(
            TrainerVersion.trainer_product_id == version_id,
            TrainerVersion.version == version_str,
        )
    )
    tver = result.scalar_one_or_none()
    if not tver:
        tver = TrainerVersion(
            trainer_product_id=version_id,
            version=version_str,
            release_status="staging",
            locale_pack_ids=["ru-RU"],
            published_at=None,
            requires_expert_review=False,
        )
        db.add(tver)
        await db.flush()
        results["version"] = 1

    # 5. Create/update localization
    locale_code = "ru-RU"
    result = await db.execute(
        select(TrainerLocalization).where(
            TrainerLocalization.trainer_product_id == trainer.id,
            TrainerLocalization.locale == locale_code,
        )
    )
    existing_locale = result.scalar_one_or_none()
    if existing_locale and locale_data:
        # Update locale strings if data changed (e.g. new/edited titles, explanations)
        existing_locale.strings = locale_data
        results["localization"] = 1
    elif not existing_locale and locale_data:
        localization = TrainerLocalization(
            trainer_product_id=trainer.id,
            locale=locale_code,
            strings=locale_data,
        )
        db.add(localization)
        await db.flush()
        results["localization"] = 1

    # 6. Create Track (single track for this trainer)
    result = await db.execute(
        select(Track).where(
            Track.trainer_product_id == trainer.id,
            Track.slug == "ba_interview_track",
        )
    )
    track = result.scalar_one_or_none()
    if not track:
        track = Track(
            trainer_product_id=trainer.id,
            slug="ba_interview_track",
            name="Business Analyst Interview",
            description="BA Interview Preparation Track",
            sort_order=0,
        )
        db.add(track)
        await db.flush()
        results["track"] = 1

    # 7. Create Modules from modules.json
    created_modules = 0
    for mod_data in modules_data:
        mod_slug = mod_data["module_id"]
        result = await db.execute(
            select(Module).where(
                Module.slug == mod_slug,
                Module.track_id == track.id,
            )
        )
        existing_mod = result.scalar_one_or_none()
        if not existing_mod:
            module = Module(
                track_id=track.id,
                slug=mod_slug,
                name=mod_data.get("title_ru", mod_slug),
                description=mod_data.get("description_ru", ""),
                sort_order=mod_data.get("sort_order", 0),
            )
            db.add(module)
            created_modules += 1
    if created_modules > 0:
        await db.flush()
        results["module"] = created_modules

    # 8. Upsert Activities from activities.json
    upserted_activities = 0
    created_activities = 0
    updated_activities = 0
    activity_ids_in_source = set()
    for act_data in activities_data:
        aid = act_data["activity_id"]
        activity_ids_in_source.add(aid)
        result = await db.execute(
            select(Activity).where(Activity.activity_id == aid)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Update existing activity — this is the critical fix for content changes
            existing.module_id = act_data["module_id"]
            existing.activity_type = act_data["activity_type"]
            existing.evaluation_mode = act_data.get("evaluation_mode", "deterministic")
            existing.difficulty = act_data.get("difficulty", "junior")
            existing.title_key = act_data["title_key"]
            existing.description_key = act_data.get("description_key")
            existing.payload = act_data["payload"]
            existing.explanation_key = act_data["explanation_key"]
            existing.order = act_data.get("order", 0)
            existing.version = act_data.get("version", "0.1.0")
            existing.migration_metadata = act_data.get("migration_metadata")
            updated_activities += 1
        else:
            activity = Activity(
                activity_id=aid,
                trainer_product_id=trainer.id,
                module_id=act_data["module_id"],
                activity_type=act_data["activity_type"],
                evaluation_mode=act_data.get("evaluation_mode", "deterministic"),
                difficulty=act_data.get("difficulty", "junior"),
                title_key=act_data["title_key"],
                description_key=act_data.get("description_key"),
                payload=act_data["payload"],
                explanation_key=act_data["explanation_key"],
                order=act_data.get("order", 0),
                version=act_data.get("version", "0.1.0"),
                migration_metadata=act_data.get("migration_metadata"),
            )
            db.add(activity)
            created_activities += 1

        upserted_activities += 1
        # Flush in batches
        if upserted_activities % 50 == 0:
            await db.flush()

    if upserted_activities > 0:
        await db.flush()
    results["activities_created"] = created_activities
    results["activities_updated"] = updated_activities
    results["activities_total"] = upserted_activities

    # Count totals
    result = await db.execute(select(Activity).where(Activity.trainer_product_id == trainer.id))
    all_acts = result.scalars().all()
    results["total_activities_after"] = len(all_acts)

    return results


def _load_json(relative_path: str) -> dict | list | None:
    """Load a JSON file from the package directory."""
    filepath = PACKAGE_DIR / relative_path
    if not filepath.exists():
        print(f"WARNING: Package file not found: {filepath}")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERROR: Failed to load {filepath}: {e}")
        return None
