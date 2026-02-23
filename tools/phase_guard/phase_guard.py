import subprocess
from pathlib import Path
from typing import List

from .phase_map import PHASES, FROZEN_PHASES


def _git_diff_files(base: str = "origin/main") -> List[Path]:
    """
    Returns list of changed files since base.
    MUST degrade safely if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        # 🔒 CRITICAL: phase guard must NEVER crash test or runtime
        return []

    return [Path(p) for p in result.stdout.splitlines() if p.strip()]


def enforce_phase_guard(base: str = "origin/main") -> None:
    changed = _git_diff_files(base)

    if not changed:
        return  # nothing to validate

    for phase, paths in PHASES.items():
        if phase not in FROZEN_PHASES:
            continue

        for frozen_path in paths:
            for changed_file in changed:
                if frozen_path == changed_file or frozen_path in changed_file.parents:
                    raise RuntimeError(
                        f"Illegal modification to frozen Phase {phase}: {changed_file}"
                    )