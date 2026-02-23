# checks/validate_structure.py
"""
Validate that strategy files live in the `strategies/` package.

This validator:
 - ignores common venv/site-packages and htmlcov noise
 - skips test files
 - detects and ignores simple one-line re-export shims that only re-export
   from strategies.strategy_base (keeps backward compatibility)

Exits with non-zero on real violations so CI can fail.
"""
import re
import sys
from pathlib import Path
from typing import Set

ROOT = Path(".").resolve()

# Path fragments to ignore (venv, system site-packages, coverage, etc.)
IGNORED_PARTS: Set[str] = {
    "venv",
    ".venv",
    "Lib",
    "site-packages",
    "htmlcov",
    "__pycache__",
}

# Regex to detect a simple re-export shim that imports from strategies.strategy_base
RE_SHIM = re.compile(r"^\s*from\s+strategies\.strategy_base\s+import\s+(.+)$")

def is_one_line_shim(path: Path) -> bool:
    """Return True if file contains only comments/blank lines and a single
    re-export from strategies.strategy_base (possibly with trailing newline)."""
    try:
        text = path.read_text(encoding="utf8")
    except Exception:
        return False
    # remove BOM and split lines
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    # If after removing blanks/comments there's exactly one line and it matches the shim regex -> OK
    if len(lines) == 1 and RE_SHIM.match(lines[0]):
        return True
    return False

violations = []

for p in ROOT.rglob("*strategy*.py"):
    try:
        rel = p.relative_to(ROOT)
    except Exception:
        # ignore weird paths we cannot relativize
        continue
    parts = set(rel.parts)
    # ignore venv/site-packages/htmlcov etc.
    if parts & IGNORED_PARTS:
        continue
    # tests are allowed to reference strategies
    if "tests" in rel.parts:
        continue
    # If file is under strategies/ it's fine
    if "strategies" in rel.parts:
        continue
    # If file is a harmless shim (single-line re-export) skip it
    if is_one_line_shim(p):
        continue
    # Otherwise report violation
    violations.append(str(rel))

if violations:
    print("Strategy placement violations:")
    for v in violations:
        print(" -", v)
    sys.exit(2)

print("Structure OK")
sys.exit(0)
