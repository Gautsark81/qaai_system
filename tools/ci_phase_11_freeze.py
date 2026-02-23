import sys
import subprocess
from pathlib import Path

FREEZE_MARKER = Path("PHASE_11_FROZEN")
PROTECTED_PATHS = [
    "model_ops/capital",
    "tests/phase_11",
    "tests/model_ops/capital",
]

def git_diff_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()

def main():
    if not FREEZE_MARKER.exists():
        return  # Phase 11 not frozen yet

    changed = git_diff_files()

    violations = [
        f for f in changed
        if any(f.startswith(p) for p in PROTECTED_PATHS)
    ]

    if violations:
        print("\n❌ PHASE-11 FREEZE VIOLATION\n")
        print("The following files are frozen after Phase-11:\n")
        for v in violations:
            print(f" - {v}")
        print("\nTo proceed, you must:")
        print("  1. Explicitly unlock Phase-12")
        print("  2. Update phase_rules.py")
        print("  3. Record a governance decision\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
