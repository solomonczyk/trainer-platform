"""Diagnose CI test failures by running pytest programmatically and printing output."""

import sys
import os
import traceback

def main():
    print("=== CI Diagnostic Script ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Environment DATABASE_URL: {os.environ.get('DATABASE_URL', '(not set)')}")
    print(f"Environment APP_ENV: {os.environ.get('APP_ENV', '(not set)')}")
    print(f"Environment DEBUG: {os.environ.get('DEBUG', '(not set)')}")

    # Check critical imports
    print("\n=== Critical imports ===")
    for mod_name in ['pytest', 'sqlalchemy', 'aiosqlite', 'asyncio', 'httpx',
                      'pydantic', 'fastapi', 'jose']:
        try:
            mod = __import__(mod_name)
            print(f"  {mod_name}: OK (version: {getattr(mod, '__version__', 'N/A')})")
        except Exception as e:
            print(f"  {mod_name}: FAILED - {e}")

    # Try loading all pytest plugins
    print("\n=== Pytest plugins ===")
    try:
        import pkg_resources
        for ep in pkg_resources.iter_entry_points('pytest11'):
            try:
                ep.load()
                print(f"  {ep.name}: OK")
            except Exception as e:
                print(f"  {ep.name}: FAILED - {e}")
    except ImportError:
        print("  pkg_resources not available (setuptools missing)")
        # Fallback: try to enumerate installed packages
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=columns'],
                capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.split('\n'):
                if 'pytest' in line.lower() or 'asyncio' in line.lower() or 'sqlalchemy' in line.lower():
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"  pip list failed: {e}")

    # App imports
    print("\n=== App imports ===")
    app_modules = [
        'app.core.config',
        'app.core.rate_limiter',
        'app.db.base',
        'app.db.session',
        'app.main',
        'app.db.models',
        'app.core.security',
    ]
    for mod_name in app_modules:
        try:
            __import__(mod_name)
            print(f"  {mod_name}: OK")
        except Exception as e:
            print(f"  {mod_name}: FAILED - {e}")
            traceback.print_exc()

    # Try running pytest programmatically on a single test
    print("\n=== Running pytest programmatically ===")
    try:
        import pytest
        exit_code = pytest.main([
            'tests/test_health_ready.py',
            '-v',
            '--tb=short',
            '-x',
            '--override-ini=asyncio_mode=auto'
        ])
        print(f"pytest exit code: {exit_code}")
        # Exit code meanings:
        exit_codes = {0: "OK", 1: "TESTS_FAILED", 2: "INTERRUPTED",
                      3: "INTERNAL_ERROR", 4: "USAGE_ERROR", 5: "NO_TESTS_COLLECTED"}
        print(f"pytest exit meaning: {exit_codes.get(exit_code, 'UNKNOWN')}")
    except Exception as e:
        print(f"pytest execution error: {e}")
        traceback.print_exc()

    # Try running full test suite
    print("\n=== Running full test suite programmatically ===")
    try:
        import pytest
        exit_code = pytest.main([
            'tests/',
            '-v',
            '--tb=short',
            '-x'
        ])
        print(f"Full suite exit code: {exit_code}")
    except Exception as e:
        print(f"Full suite error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
