import json
import sys
from pathlib import Path

STATUS_FILE = Path("project_super_status.json")
READINESS_FILE = Path("RELEASE_READINESS.md")

BLOCKERS = []

def fail(msg):
    BLOCKERS.append(msg)

def main():
    if not STATUS_FILE.exists():
        fail("Missing project_super_status.json")

    if not READINESS_FILE.exists():
        fail("Missing RELEASE_READINESS.md")

    data = json.loads(STATUS_FILE.read_text())

    phase_a = data["phase_status"]["Phase A"]["status"]
    if phase_a != "complete":
        fail("Phase A is not complete")

    risky = [
        f for f in data["files"].values()
        if "background_task" in f.get("risks", [])
    ]
    if risky:
        fail(f"Background tasks detected: {len(risky)} files")

    if BLOCKERS:
        print("❌ RELEASE BLOCKED")
        for b in BLOCKERS:
            print(" -", b)
        sys.exit(1)

    print("✅ RELEASE APPROVED")

if __name__ == "__main__":
    main()
