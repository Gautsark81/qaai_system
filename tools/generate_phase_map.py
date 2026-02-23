# tools/generate_phase_map.py

import json
from pathlib import Path
from phase_resolver import EXECUTION_PHASES, ARCH_PHASES

ROOT = Path(__file__).resolve().parents[1]

def generate():
    phase_map = {}

    for base in ["modules", "model_ops"]:
        root = ROOT / base
        if not root.exists():
            continue

        for d in root.iterdir():
            if not d.is_dir():
                continue

            name = d.name
            phase = EXECUTION_PHASES.get(name) or ARCH_PHASES.get(name)
            if phase:
                phase_map[str(d.relative_to(ROOT))] = phase

    return phase_map


if __name__ == "__main__":
    phase_map = generate()
    with open("phase_map.auto.json", "w") as f:
        json.dump(phase_map, f, indent=2, sort_keys=True)

    print("✅ phase_map.auto.json generated")
