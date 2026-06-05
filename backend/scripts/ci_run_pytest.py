"""Run pytest via subprocess and capture ALL output for CI debugging."""

import subprocess
import sys


def run_pytest(cmd, label):
    print(f"\n=== Running: {label} ===")
    print(f"Command: {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    print(f"stdout ({len(result.stdout)} bytes):")
    if result.stdout:
        print(result.stdout)
    else:
        print("  (empty)")
    print(f"stderr ({len(result.stderr)} bytes):")
    if result.stderr:
        print(result.stderr)
    else:
        print("  (empty)")
    if result.returncode != 0:
        print("::error::{} exit_code={} stdout_len={} stderr_len={}".format(
            label, result.returncode, len(result.stdout), len(result.stderr)))
        if result.stderr:
            err = result.stderr
            for i in range(0, len(err), 300):
                chunk = err[i:i+300]
                print("::warning file=pytest.log,line={}::{}".format(
                    i // 300 + 1, chunk.replace("\n", "\\n").replace("\r", "\\r")))
    return result


if __name__ == "__main__":
    py = sys.executable

    # Test 1: minimal command (--override-ini, --collect-only, single file)
    run_pytest(
        [py, "-m", "pytest", "--override-ini=asyncio_mode=auto",
         "--collect-only", "tests/test_health_ready.py", "-q"],
        "minimal --override-ini single file collect-only"
    )

    # Test 2: the exact command that fails (no --override-ini, full tests/, verbose)
    run_pytest(
        [py, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
        "full suite (same as Run tests step)"
    )

    # Test 3: same as Test 2 but with --override-ini
    run_pytest(
        [py, "-m", "pytest", "--override-ini=asyncio_mode=auto",
         "tests/", "-v", "--tb=short", "-x"],
        "full suite with --override-ini"
    )

    # Always succeed so we can read the annotations
    sys.exit(0)
