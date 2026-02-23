import json
from pathlib import Path

OLD = Path("project_super_status.prev.json")
NEW = Path("project_super_status.json")

if not OLD.exists():
    print("No previous scan found. Save current as baseline.")
    OLD.write_text(NEW.read_text())
    exit(0)

old = json.loads(OLD.read_text())
new = json.loads(NEW.read_text())

print("📊 PHASE DELTA\n")

for phase in new["phase_confidence_computed"]:
    o = old["phase_confidence_computed"].get(phase, 0)
    n = new["phase_confidence_computed"][phase]
    delta = round(n - o, 3)
    print(f"{phase}: {o} → {n} ({'+' if delta>=0 else ''}{delta})")

OLD.write_text(NEW.read_text())
