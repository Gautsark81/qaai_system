# scripts/merge_strategy_folders.py
"""
Merge files from 'strategy/' into the canonical 'strategies/' package.

- Copies .py files from strategy/ into strategies/
- Creates strategies/__init__.py if missing
- Avoids clobbering by default: if file exists, writes with suffix '.from_strategy'
- Prints summary and exit code 0 on success.
"""
import os
import shutil
from pathlib import Path

ROOT = Path.cwd()
src = ROOT / "strategy"
dst = ROOT / "strategies"

if not src.exists():
    print("Source folder 'strategy/' not found. Nothing to merge.")
    raise SystemExit(1)

dst.mkdir(parents=True, exist_ok=True)

# ensure package __init__.py exists
init_file = dst / "__init__.py"
if not init_file.exists():
    init_file.write_text("# Auto-generated package init for strategies\n")
    print(f"Created {init_file}")

copied = []
skipped = []
overwritten = []
for p in src.glob("*.py"):
    target = dst / p.name
    if target.exists():
        # avoid destructive overwrite: create alternate name
        alt = dst / (p.stem + ".from_strategy.py")
        shutil.copy2(p, alt)
        copied.append(str(alt))
        print(f"Copied (alternate) {p} -> {alt}")
    else:
        shutil.copy2(p, target)
        copied.append(str(target))
        print(f"Copied {p} -> {target}")

# also copy subpackages (recursively) if any
for sub in src.iterdir():
    if sub.is_dir():
        tgt_sub = dst / sub.name
        if tgt_sub.exists():
            print(f"Skipping existing subfolder {sub}")
            continue
        shutil.copytree(sub, tgt_sub)
        print(f"Copied directory {sub} -> {tgt_sub}")

print("\nMerge complete.")
print(f"Files copied: {len(copied)}")
