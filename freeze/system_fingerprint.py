import hashlib
import os
from pathlib import Path
from typing import Iterable


# 🔒 Explicit, audited source roots only
DEFAULT_INCLUDED_DIRS = (
    "core",
    "domain",
    "modules",
    "intelligence",
    "execution",
    "data",
    "capital",
    "chaos",
    "freeze",
    "audit",
    "runbook",
    "optimization",
    "simulation",
)

# 🚫 Hard exclusions
EXCLUDED_DIR_NAMES = {
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".idea",
    ".vscode",
    "logs",
    "artifacts",
    "data_cache",
}


def _iter_source_files(
    root: Path,
    include_dirs: Iterable[str],
):
    for dirname in include_dirs:
        base = root / dirname
        if not base.exists():
            continue

        for path in base.rglob("*.py"):
            if any(p in EXCLUDED_DIR_NAMES for p in path.parts):
                continue
            yield path


def compute_system_checksum(
    project_root: str | Path = ".",
    include_dirs: Iterable[str] = DEFAULT_INCLUDED_DIRS,
) -> str:
    """
    Compute a deterministic checksum of *source code only*.

    - No virtualenv
    - No caches
    - No runtime artifacts
    - Safe for CI
    """
    root = Path(project_root).resolve()
    sha = hashlib.sha256()

    for path in sorted(_iter_source_files(root, include_dirs)):
        sha.update(path.read_bytes())

    return sha.hexdigest()
