"""Seed BA Phase 2 scenario content into the database.

Phase 2 scenarios use the Scenario model (not the Activity model) because they
are AI-evaluated free-text assignments, not deterministic activities.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Domain, Rubric, RubricCriterion, Scenario,
    Skill, SkillMap, TrainerProduct,
)

PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "trainer_packages" / "business_analyst_interview_trainer"


async def seed_ba_phase2(db: AsyncSession, inline: object = None) -> dict:
    """Seed BA Phase 2 scenarios and rubrics.

    Args:
        db: Database session.
        inline: Optional ``InlineSeedRequest`` with ``scenarios_data`` and
            ``rubrics_data`` overriding file-based loading.

    Returns:
        A dict with counts of created records, or an error dict.
    """
    results = {"scenarios": 0, "rubrics": 0, "criteria": 0, "skills": 0, "skill_map": 0}

    # 1. Load Phase 2 data files (or use inline data)
    if inline and getattr(inline, "scenarios_data", None):
        scenarios_data = inline.scenarios_data
    else:
        scenarios_data = _load_json("phase2_scenarios.json")

    if inline and getattr(inline, "rubrics_data", None):
        rubrics_data = inline.rubrics_data
    else:
        rubrics_data = _load_json("phase2_rubrics.json")

    if not scenarios_data:
        return {"error": "Failed to load phase2_scenarios.json"}
    if not rubrics_data:
        return {"error": "Failed to load phase2_rubrics.json"}

    # 2. Resolve the BA trainer product
    result = await db.execute(
        select(TrainerProduct).where(
            TrainerProduct.trainer_product_id == "business_analyst_interview_trainer"
        )
    )
    trainer = result.scalar_one_or_none()
    if not trainer:
        return {"error": "BA trainer product not found - seed Phase 1 first"}

    # 3. Seed skills for Phase 2
    skill_data = rubrics_data.get("skills", _default_phase2_skills())
    created_skills = 0
    for skill_info in skill_data:
        sid = skill_info["skill_id"]
        result = await db.execute(select(Skill).where(Skill.skill_id == sid))
        existing = result.scalar_one_or_none()
        if not existing:
            skill = Skill(
                skill_id=sid,
                name=skill_info["name"],
                category=skill_info.get("category", "ba_core"),
                levels=skill_info.get("levels"),
                description=skill_info.get("description"),
            )
            db.add(skill)
            created_skills += 1
    if created_skills > 0:
        await db.flush()
    results["skills"] = created_skills

    # 4. Seed skill map
    skill_map_id = rubrics_data.get("rubric_pack_id", "ba_phase2_rubric_pack_v1")
    result = await db.execute(
        select(SkillMap).where(SkillMap.skill_map_id == skill_map_id)
    )
    existing_sm = result.scalar_one_or_none()
    if not existing_sm:
        sm = SkillMap(
            skill_map_id=skill_map_id,
            skills=skill_data,
        )
        db.add(sm)
        await db.flush()
        results["skill_map"] = 1

    # 5. Seed rubrics and criteria
    created_rubrics = 0
    created_criteria = 0
    for rubric_info in rubrics_data.get("rubrics", []):
        rid = rubric_info["rubric_id"]
        result = await db.execute(select(Rubric).where(Rubric.rubric_id == rid))
        existing_r = result.scalar_one_or_none()
        if existing_r:
            continue

        rubric = Rubric(
            rubric_id=rid,
            scenario_id=None,  # Set after scenario is created
            pass_score=rubric_info.get("pass_score", 70),
            critical_fail_enabled=rubric_info.get("critical_fail_enabled", True),
        )
        db.add(rubric)
        await db.flush()
        created_rubrics += 1

        # Create criteria
        for c_info in rubric_info.get("criteria", []):
            criterion = RubricCriterion(
                rubric_id=rubric.id,
                criterion_id=c_info["criterion_id"],
                name=c_info["name"],
                weight=c_info["weight"],
                evidence_required=True,
            )
            db.add(criterion)
            created_criteria += 1

    if created_criteria > 0:
        await db.flush()
    results["rubrics"] = created_rubrics
    results["criteria"] = created_criteria

    # 6. Seed scenarios
    created_scenarios = 0
    for sc_data in scenarios_data:
        sid = sc_data["scenario_id"]
        result = await db.execute(
            select(Scenario).where(Scenario.scenario_id == sid)
        )
        existing_s = result.scalar_one_or_none()
        if existing_s:
            continue

        # Resolve rubric FK
        rubric = None
        rid = sc_data.get("rubric_id")
        if rid:
            result = await db.execute(select(Rubric).where(Rubric.rubric_id == rid))
            rubric = result.scalar_one_or_none()

        scenario = Scenario(
            scenario_id=sid,
            trainer_product_id=trainer.id,
            title_key=sc_data["title_key"],
            goal_key=sc_data["task"][:200],  # Use first 200 chars of task as goal
            trainer_version="0.2.0",
            track="ba_interview_track",
            module=sc_data.get("module_id", "ba_real_cases"),
            difficulty="intermediate",
            estimated_duration_minutes=sc_data.get("estimated_minutes", 30),
            target_skills=_scenario_skills(sid),
            user_role="business_analyst",
            ai_role="evaluator",
            rubric_id=rid,
            steps=[{
                "step_id": f"{sid}_step1",
                "order": 1,
                "prompt_key": sc_data.get("task", ""),
            }],
            hints=_build_hints(sc_data),
            status="published_seed",
        )
        db.add(scenario)
        await db.flush()
        created_scenarios += 1

        # Link rubric to scenario
        if rubric:
            rubric.scenario_id = scenario.id

    if created_scenarios > 0:
        await db.flush()
    results["scenarios"] = created_scenarios

    return results


async def seed_ba_phase2_all(db: AsyncSession) -> dict:
    """Run all Phase 2 seeding steps.

    Combines Phase 2 scenario + rubric seeding.
    """
    return await seed_ba_phase2(db)


def _default_phase2_skills() -> list[dict]:
    """Return default Phase 2 skill definitions."""
    return [
        {
            "skill_id": "ba_stakeholder_analysis",
            "name": "Stakeholder Analysis",
            "category": "ba_core",
            "description": "Ability to identify, analyze, and manage stakeholders",
        },
        {
            "skill_id": "ba_requirements_engineering",
            "name": "Requirements Engineering",
            "category": "ba_core",
            "description": "Elicitation, analysis, specification, and validation of requirements",
        },
        {
            "skill_id": "ba_process_modeling",
            "name": "Process & Data Modeling",
            "category": "ba_core",
            "description": "AS-IS/TO-BE analysis, BPMN, process improvement",
        },
        {
            "skill_id": "ba_documentation",
            "name": "Documentation & Artifacts",
            "category": "ba_core",
            "description": "BRD, SRS, user stories, acceptance criteria",
        },
        {
            "skill_id": "ba_communication",
            "name": "Communication & Conflict Resolution",
            "category": "soft_skills",
            "description": "Stakeholder communication, conflict management, facilitation",
        },
        {
            "skill_id": "ba_analytical_thinking",
            "name": "Analytical Thinking & Problem Solving",
            "category": "ba_core",
            "description": "Impact analysis, risk assessment, solution design",
        },
    ]


def _scenario_skills(scenario_id: str) -> list[str]:
    """Map scenario IDs to relevant skill IDs."""
    mapping = {
        "ba_phase2_stakeholder_requirements": ["ba_stakeholder_analysis", "ba_requirements_engineering", "ba_communication"],
        "ba_phase2_process_analysis": ["ba_process_modeling", "ba_analytical_thinking"],
        "ba_phase2_documentation_artifacts": ["ba_documentation", "ba_requirements_engineering"],
        "ba_phase2_conflict_resolution": ["ba_communication", "ba_stakeholder_analysis"],
        "ba_phase2_traceability_impact": ["ba_analytical_thinking", "ba_documentation"],
        "ba_phase2_real_case_analysis": ["ba_analytical_thinking", "ba_documentation", "ba_requirements_engineering"],
    }
    return mapping.get(scenario_id, ["ba_analytical_thinking"])


def _build_hints(sc_data: dict) -> list[str]:
    """Build hints from constraints."""
    hints = []
    constraints = sc_data.get("constraints", [])
    for c in constraints[:3]:
        hints.append(f"Учтите ограничение: {c}")
    hints.append(f"Рекомендуемое время: {sc_data.get('estimated_minutes', 30)} минут")
    return hints


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
