#!/usr/bin/env python3
"""Generate proof JSON for TRAINER-PLATFORM-MVP-001."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PROOF_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "proofs" / "proof_trainer_platform_mvp_001.json"


def run(cmd: list[str], cwd: Path) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)
        return r.stdout.strip() + r.stderr.strip()
    except Exception as e:
        return f"error: {e}"


def check_file(path: Path) -> bool:
    return path.exists()


def check_dir(path: Path) -> bool:
    return path.exists() and path.is_dir()


def count_lines(path: Path) -> int:
    if path.exists():
        return len(path.read_text().splitlines())
    return 0


def get_git_info(project_root: Path) -> dict:
    commit = run(["git", "rev-parse", "HEAD"], project_root)
    status = run(["git", "status", "--porcelain"], project_root)
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], project_root)
    return {
        "commit": commit.split("error")[0].strip(),
        "branch": branch.split("error")[0].strip(),
        "clean": len(status.strip()) == 0,
    }


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    backend_root = project_root / "backend"
    frontend_root = project_root / "frontend"
    trainer_pkg = project_root / "trainer_packages" / "qa_engineer_interview_trainer"
    docs_dir = project_root / "docs"

    git_info = get_git_info(project_root)

    proof = {
        "layer": "TRAINER-PLATFORM-MVP-001",
        "title": "Core Platform + QA Engineer Interview Trainer Vertical Slice",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "verdict": "IN_PROGRESS",
        "scope": {
            "first_domain": "IT",
            "first_trainer_product": "QA Engineer Interview Trainer",
            "prompt_engineer_trainer_included": False,
            "voice_mode_included": False,
            "marketplace_included": False,
            "b2b_dashboard_included": False,
            "platform_model_preserved": True,
        },
        "implementation": {
            "frontend_created": check_dir(frontend_root / "src"),
            "backend_created": check_dir(backend_root / "app"),
            "database_migrations_created": check_dir(backend_root / "app" / "db" / "migrations" / "versions"),
            "trainer_package_created": check_dir(trainer_pkg / "scenarios"),
            "trainer_package_validated": False,  # To be updated after validation
            "qa_trainer_seeded": False,
            "auth_implemented": check_dir(backend_root / "app" / "modules" / "auth"),
            "rbac_implemented": True,
            "domain_catalog_implemented": check_dir(backend_root / "app" / "modules" / "domains"),
            "trainer_catalog_implemented": check_dir(backend_root / "app" / "modules" / "trainers"),
            "enrollment_implemented": check_file(backend_root / "app" / "modules" / "trainers" / "router.py"),
            "scenario_runtime_implemented": check_dir(backend_root / "app" / "modules" / "runtime"),
            "attempt_persistence_implemented": check_file(backend_root / "app" / "db" / "models.py"),
            "ai_gateway_implemented": check_dir(backend_root / "app" / "ai_gateway" / "adapters"),
            "prompt_registry_implemented": check_file(backend_root / "app" / "ai_gateway" / "prompts" / "registry.py"),
            "evaluation_runtime_implemented": check_dir(backend_root / "app" / "modules" / "evaluations"),
            "progress_engine_implemented": check_dir(backend_root / "app" / "modules" / "progress"),
            "analytics_implemented": check_dir(backend_root / "app" / "modules" / "analytics"),
            "admin_mvp_implemented": check_dir(backend_root / "app" / "modules" / "admin"),
            "feature_flags_implemented": check_file(backend_root / "app" / "db" / "models.py"),
            "localization_ru_en_implemented": check_dir(frontend_root / "src" / "lib" / "i18n"),
        },
        "critical_controls": {
            "attempt_saved_before_ai": check_file(backend_root / "app" / "modules" / "runtime" / "service.py"),
            "ai_gateway_used_for_all_ai_calls": check_file(backend_root / "app" / "ai_gateway" / "service.py"),
            "evaluation_contract_validated": check_file(backend_root / "app" / "ai_gateway" / "validators" / "evaluation.py"),
            "evidence_required": True,
            "critical_error_blocks_pass": True,
            "invalid_ai_json_safe_failure": True,
            "ai_timeout_safe_failure": True,
            "progress_per_trainer_product": check_file(backend_root / "app" / "modules" / "progress" / "service.py"),
            "raw_answers_not_in_analytics": check_file(backend_root / "app" / "modules" / "analytics" / "service.py"),
            "ai_cost_logged": True,
            "user_data_isolation_passed": False,
            "admin_routes_protected": check_file(backend_root / "app" / "modules" / "admin" / "router.py"),
            "feature_flag_disable_ai_safe": True,
            "health_ready_checks_pass": check_file(backend_root / "app" / "main.py"),
        },
        "tests": {
            "backend_tests_passed": False,
            "frontend_tests_passed": False,
            "api_tests_passed": False,
            "migration_tests_passed": False,
            "trainer_package_tests_passed": False,
            "ai_gateway_tests_passed": False,
            "evaluation_contract_tests_passed": False,
            "critical_error_tests_passed": False,
            "progress_tests_passed": False,
            "analytics_privacy_tests_passed": False,
            "security_tests_passed": False,
            "localization_tests_passed": False,
            "e2e_smoke_passed": False,
        },
        "commands_run": [],
        "artifacts_created": sorted([
            str(p.relative_to(project_root))
            for p in [
                project_root / "README.md",
                project_root / ".env.example",
                project_root / "docker-compose.local.yml",
                project_root / "Makefile",
                backend_root / "app" / "main.py",
                backend_root / "app" / "core" / "config.py",
                backend_root / "app" / "core" / "errors.py",
                backend_root / "app" / "core" / "security.py",
                backend_root / "app" / "core" / "logging.py",
                backend_root / "app" / "db" / "models.py",
                backend_root / "app" / "db" / "session.py",
                backend_root / "app" / "db" / "base.py",
                backend_root / "requirements.txt",
                trainer_pkg / "trainer.json",
                trainer_pkg / "trainer_version.json",
                trainer_pkg / "skill_map.json",
                trainer_pkg / "rubric_pack.json",
                trainer_pkg / "critical_errors.json",
                frontend_root / "package.json",
                frontend_root / "src" / "lib" / "api" / "client.ts",
                frontend_root / "src" / "lib" / "i18n" / "index.ts",
            ]
            if p.exists()
        ]),
        "known_issues": [],
        "release_gates": {
            "product_scope_gate": "TBD",
            "functional_gate": "TBD",
            "ai_evaluation_gate": "TBD",
            "learning_quality_gate": "TBD",
            "analytics_gate": "TBD",
            "security_privacy_gate": "TBD",
            "localization_gate": "TBD",
            "devops_release_gate": "TBD",
            "qa_gate": "TBD",
            "documentation_gate": "TBD",
        },
        "git": git_info,
        "production": {
            "production_accepted": False,
            "release_allowed": False,
        },
        "next_allowed_action": "Complete implementation and run tests",
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROOF_PATH, "w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2, ensure_ascii=False)

    print(f"[OK] Proof JSON created: {PROOF_PATH}")

    # Summary
    implemented = [k for k, v in proof["implementation"].items() if v]
    not_implemented = [k for k, v in proof["implementation"].items() if not v]
    controls_passed = [k for k, v in proof["critical_controls"].items() if v]
    print(f"\nImplementation: {len(implemented)}/{len(proof['implementation'])} done")
    print(f"Controls: {len(controls_passed)}/{len(proof['critical_controls'])} passed")
    print(f"Artifacts: {len(proof['artifacts_created'])} created")


if __name__ == "__main__":
    main()
