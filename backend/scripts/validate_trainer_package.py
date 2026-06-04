#!/usr/bin/env python3
"""Validate a trainer package directory for structural and content correctness."""

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_package(package_dir: Path) -> list[str]:
    errors = []

    # Required files
    required_files = [
        "trainer.json",
        "trainer_version.json",
        "skill_map.json",
        "rubric_pack.json",
        "critical_errors.json",
    ]
    for fname in required_files:
        if not (package_dir / fname).exists():
            errors.append(f"MISSING: {fname}")

    if errors:
        return errors

    # Check trainer.json
    trainer = load_json(package_dir / "trainer.json")
    for field in ["trainer_product_id", "domain", "slug", "name", "default_locale", "supported_locales"]:
        if field not in trainer:
            errors.append(f"trainer.json: missing field '{field}'")

    # Check trainer_version.json
    version = load_json(package_dir / "trainer_version.json")
    for field in ["trainer_product_id", "version", "skill_map_id", "rubric_pack_id", "scenario_ids"]:
        if field not in version:
            errors.append(f"trainer_version.json: missing field '{field}'")

    # Check skill_map.json
    skill_map = load_json(package_dir / "skill_map.json")
    if "skills" not in skill_map or not isinstance(skill_map["skills"], list):
        errors.append("skill_map.json: 'skills' must be a list")
    else:
        skill_ids = set()
        for skill in skill_map["skills"]:
            if "skill_id" not in skill:
                errors.append(f"skill_map.json: skill missing 'skill_id'")
            else:
                skill_ids.add(skill["skill_id"])
            if "name" not in skill:
                errors.append(f"skill_map.json: skill '{skill.get('skill_id', '?')}' missing 'name'")

    # Check rubric_pack.json
    rubric_pack = load_json(package_dir / "rubric_pack.json")
    if "rubrics" not in rubric_pack or not isinstance(rubric_pack["rubrics"], list):
        errors.append("rubric_pack.json: 'rubrics' must be a list")
    else:
        rubric_ids = set()
        for rubric in rubric_pack["rubrics"]:
            rid = rubric.get("rubric_id", "?")
            if rid in rubric_ids:
                errors.append(f"rubric_pack.json: duplicate rubric_id '{rid}'")
            rubric_ids.add(rid)
            if "criteria" not in rubric or not isinstance(rubric["criteria"], list):
                errors.append(f"rubric '{rid}': missing 'criteria'")
            else:
                total_weight = sum(c.get("weight", 0) for c in rubric["criteria"])
                if total_weight != 100:
                    errors.append(f"rubric '{rid}': criteria weights sum to {total_weight}, expected 100")
                for c in rubric["criteria"]:
                    if "criterion_id" not in c:
                        errors.append(f"rubric '{rid}': criterion missing 'criterion_id'")
                    if c.get("evidence_required", True) and "evidence_required" not in c:
                        pass  # default is True

    # Check critical_errors.json
    crit_errors = load_json(package_dir / "critical_errors.json")
    if "critical_errors" not in crit_errors or not isinstance(crit_errors["critical_errors"], list):
        errors.append("critical_errors.json: 'critical_errors' must be a list")
    else:
        error_ids = set(e["error_id"] for e in crit_errors["critical_errors"] if "error_id" in e)
        if not error_ids:
            errors.append("critical_errors.json: no error_id found")

    # Check scenarios directory
    scenarios_dir = package_dir / "scenarios"
    if not scenarios_dir.exists():
        errors.append("MISSING: scenarios/ directory")
    else:
        scenario_files = list(scenarios_dir.glob("*.json"))
        if not scenario_files:
            errors.append("scenarios/: no JSON files found")
        scenario_ids = set()
        for sf in scenario_files:
            try:
                scenario = load_json(sf)
                sid = scenario.get("scenario_id", "?")
                if sid in scenario_ids:
                    errors.append(f"scenarios/{sf.name}: duplicate scenario_id '{sid}'")
                scenario_ids.add(sid)
                # Check rubric reference
                if "rubric_id" in scenario and scenario["rubric_id"] not in rubric_ids:
                    errors.append(f"scenario '{sid}': references unknown rubric '{scenario['rubric_id']}'")
                # Check skill references
                if "target_skills" in scenario:
                    for sk in scenario["target_skills"]:
                        sk_id = sk if isinstance(sk, str) else sk.get("skill_id", "")
                        if sk_id not in skill_ids:
                            errors.append(f"scenario '{sid}': references unknown skill '{sk_id}'")
                # Check critical error references
                if "critical_errors" in scenario:
                    for ce in scenario["critical_errors"]:
                        if ce not in error_ids:
                            errors.append(f"scenario '{sid}': references unknown critical error '{ce}'")
            except json.JSONDecodeError as e:
                errors.append(f"scenarios/{sf.name}: invalid JSON - {e}")

    # Check locales
    locales_dir = package_dir / "locales"
    if not locales_dir.exists():
        errors.append("MISSING: locales/ directory")
    else:
        supported = trainer.get("supported_locales", [])
        for loc in supported:
            if not (locales_dir / f"{loc}.json").exists():
                errors.append(f"locales/: missing '{loc}.json' for supported locale")
        # Check locale keys cover scenario titles
        locale_files = list(locales_dir.glob("*.json"))
        for lf in locale_files:
            locale_data = load_json(lf)
            strings = locale_data.get("strings", {})
            # Check if scenario title_keys are present
            scenario_files = list(scenarios_dir.glob("*.json")) if scenarios_dir.exists() else []
            for sf in scenario_files:
                try:
                    scenario = load_json(sf)
                    title_key = scenario.get("title_key", "")
                    if title_key and title_key not in strings:
                        errors.append(f"locales/{lf.name}: missing key '{title_key}' for scenario '{scenario.get('scenario_id', '?')}'")
                    goal_key = scenario.get("goal_key", "")
                    if goal_key and goal_key not in strings:
                        errors.append(f"locales/{lf.name}: missing goal key '{goal_key}'")
                except json.JSONDecodeError:
                    pass

    # Check golden_answers
    golden_dir = package_dir / "golden_answers"
    if golden_dir.exists():
        for gf in golden_dir.glob("*.json"):
            try:
                golden = load_json(gf)
                cases = golden.get("cases", [])
                for case in cases:
                    if case.get("scenario_id") not in scenario_ids:
                        errors.append(f"golden_answers/{gf.name}: case references unknown scenario '{case.get('scenario_id')}'")
            except json.JSONDecodeError:
                pass

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_trainer_package.py <package_dir>")
        sys.exit(1)

    package_dir = Path(sys.argv[1])
    if not package_dir.exists():
        print(f"ERROR: Package directory not found: {package_dir}")
        sys.exit(1)

    print(f"Validating trainer package: {package_dir}")
    errors = validate_package(package_dir)

    if errors:
        print(f"\n[FAIL] VALIDATION FAILED — {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n[OK] VALIDATION PASSED — Package is valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
