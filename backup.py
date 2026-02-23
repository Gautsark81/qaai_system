import os
import shutil
import re
from pathlib import Path


def backup_and_fix_py_files(src_dir: Path, backup_dir: Path):
    backup_dir.mkdir(parents=True, exist_ok=True)

    patterns = [
        (
            r"from signal_engine import SignalEngine",
            "from modules.signal_engine import SignalEngine",
        ),
        (
            r"from signal\.quality_control import",
            "from screening.quality_control import",
        ),
        (
            r"from signal\.signal_generator import",
            "from screening.signal_generator import",
        ),
    ]

    for src_path in src_dir.rglob("*.py"):
        relative = src_path.relative_to(src_dir)
        safe_name = str(relative).replace(os.sep, "_")
        dest = backup_dir / safe_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest)

        # Handle potential decoding issues
        content = src_path.read_text(encoding="utf-8", errors="ignore")

        for pattern, repl in patterns:
            content = re.sub(pattern, repl, content)

        fixed = [
            line for line in content.splitlines() if not re.match(r"^\s*---\s*$", line)
        ]

        src_path.write_text("\n".join(fixed), encoding="utf-8")
