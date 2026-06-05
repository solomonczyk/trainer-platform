"""Run pytest via subprocess and capture ALL output for CI debugging."""

import subprocess
import sys

if __name__ == "__main__":
    cmd = [sys.executable, "-m", "pytest", "--override-ini=asyncio_mode=auto",
           "--collect-only", "tests/test_health_ready.py", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("=== pytest STDOUT ===")
    out = result.stdout
    if len(out) > 2000:
        print("(truncated, showing last 2000 chars)")
        print(out[-2000:])
    else:
        print(out)

    print("=== pytest STDERR ===")
    err = result.stderr
    if len(err) > 2000:
        print("(truncated, showing last 2000 chars)")
        print(err[-2000:])
    else:
        print(err)

    print("=== EXIT CODE:", result.returncode, "===")
    print("stdout_len:", len(result.stdout), "stderr_len:", len(result.stderr))

    if result.returncode != 0:
        print("::error::pytest exit_code={} stdout_len={} stderr_len={}".format(
            result.returncode, len(result.stdout), len(result.stderr)))
        if result.stdout:
            print("STDOUT_FIRST_500:", result.stdout[:500])
        if result.stderr:
            print("STDERR_FIRST_500:", result.stderr[:500])

    # Don't exit with pytest's code so the step succeeds and we can see output
    sys.exit(0)
