#!/usr/bin/env python3
# tools/verify_phases0_4.py
"""
Run an automated verification for Phase 0..4:
- pytest (all)
- flake8
- mypy

Produces a 'verify_report.txt' summary in repo root.
"""

import subprocess
import sys
from pathlib import Path

REPORT = Path("verify_report.txt")


def run(cmd, capture=False):
    print(f">>> Running: {cmd}")
    try:
        if capture:
            out = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, text=True
            )
            return 0, out
        else:
            res = subprocess.run(cmd, shell=True)
            return res.returncode, None
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output


def main():
    steps = [
        ("pytest all tests", "pytest -q"),
        ("flake8 lint", "flake8 ."),
        ("mypy type check", "mypy ."),
    ]

    results = []
    for name, cmd in steps:
        rc, out = run(cmd, capture=True)
        ok = rc == 0
        results.append((name, ok, rc, out or ""))
        print(f"--- {name}: {'OK' if ok else 'FAILED'} (rc={rc})")

    # Write report
    with REPORT.open("w", encoding="utf-8") as f:
        f.write("Phase 0-4 Verification Report\n")
        f.write("=============================\n\n")
        for name, ok, rc, out in results:
            f.write(f"{name}: {'OK' if ok else 'FAILED'} (rc={rc})\n")
            if not ok:
                f.write("--- Output ---\n")
                f.write(out + "\n")
                f.write("--------------\n\n")
    print(f"\nReport written to {REPORT.resolve()}")
    # Exit nonzero if anything failed
    if any(not ok for _, ok, _, _ in results):
        print("One or more verification steps failed. See verify_report.txt")
        sys.exit(2)
    print("All verification steps passed.")


if __name__ == "__main__":
    main()
