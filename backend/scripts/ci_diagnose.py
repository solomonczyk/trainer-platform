"""Diagnose CI test failures by running pytest and capturing ALL output."""

import sys
import os
import traceback
from io import StringIO

# GitHub Actions step summary file
summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
_summary_file = None


def log(msg=""):
    """Print to stdout AND append to GITHUB_STEP_SUMMARY if available."""
    print(msg)
    global _summary_file
    if summary_path and _summary_file is None:
        try:
            _summary_file = open(summary_path, "a", encoding="utf-8")
        except Exception:
            _summary_file = False
    if _summary_file and _summary_file is not False:
        _summary_file.write(msg + "\n")
        _summary_file.flush()


def main():
    log("### CI Diagnostic Report")
    log("")
    log(f"**Python:** {sys.version}")
    log(f"**CWD:** {os.getcwd()}")
    log(f"**DATABASE_URL:** {os.environ.get('DATABASE_URL', '(not set)')}")
    log(f"**APP_ENV:** {os.environ.get('APP_ENV', '(not set)')}")
    log(f"**DEBUG:** {os.environ.get('DEBUG', '(not set)')}")

    # --- Critical imports ---
    log("")
    log("### Critical imports")
    for mod_name in ['pytest', 'sqlalchemy', 'aiosqlite', 'asyncio', 'httpx']:
        try:
            mod = __import__(mod_name)
            log(f"- {mod_name}: OK (v{getattr(mod, '__version__', '?')})")
        except Exception as e:
            log(f"- {mod_name}: FAILED - {e}")

    # --- Pytest plugins ---
    log("")
    log("### Pytest plugins")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=columns'],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if 'pytest' in line.lower() or 'timeout' in line.lower():
                log(f"- {line.strip()}")
    except Exception as e:
        log(f"- pip list failed: {e}")

    # --- App imports (quick check, not full) ---
    log("")
    log("### App imports")
    for mod_name in ['app.core.config', 'app.db.base', 'app.main']:
        try:
            __import__(mod_name)
            log(f"- {mod_name}: OK")
        except Exception as e:
            log(f"- {mod_name}: FAILED - {e}")

    # --- Run pytest on a single file only ---
    log("")
    log("### pytest: single file (test_health_ready)")
    log("<details><summary>Click to expand</summary>")
    log("")
    log("```")
    # Capture pytest output
    old_stdout = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        import pytest
        ec = pytest.main(['tests/test_health_ready.py', '-v', '--tb=short', '-x',
                          '--override-ini=asyncio_mode=auto'])
        sys.stdout = old_stdout
        log(buf.getvalue())
        log("```")
        log(f"Exit code: {ec}")
    except Exception as e:
        sys.stdout = old_stdout
        log(f"pytest exception: {e}")
        log("```")

    log("</details>")

    # --- Run full suite ---
    log("")
    log("### pytest: full suite")
    log("<details><summary>Click to expand</summary>")
    log("")
    log("```")
    sys.stdout = buf = StringIO()
    try:
        ec = pytest.main(['tests/', '-v', '--tb=short', '-x'])
        sys.stdout = old_stdout
        log(buf.getvalue())
        log("```")
        log(f"Exit code: {ec}")
    except Exception as e:
        sys.stdout = old_stdout
        log(f"pytest exception: {e}")
        log("```")
    log("</details>")


if __name__ == "__main__":
    main()
    # Clean up
    if _summary_file and _summary_file is not False:
        _summary_file.close()
    sys.exit(0)  # Always succeed so we can read the summary
