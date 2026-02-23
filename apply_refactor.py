# apply_refactor.py
from pathlib import Path
import shutil

DRY_RUN = True  # set to False to actually move files

ROOT = Path(".").resolve()
SRC = ROOT / "src" / "qaai"
MAPS = [
    ("backtest", "backtesting"),
    ("backtester", "backtesting"),
    ("screening", "screening"),
    ("screener", "screening"),
    ("streamlit_app", "apps/streamlit"),
    ("dashboard", "apps/streamlit"),
    ("broker", "infra/broker"),
    ("db", "infra/db"),
    ("orchestrator", "orchestrator"),
    ("features", "features"),
    ("data", "data"),
    ("execution", "execution"),
    ("portfolio", "portfolio"),
    ("signal_engine", "signal_engine"),
    ("strategy", "strategy"),
    ("utils", "utils"),
]


def move_dir(src_name, dest_rel):
    src = ROOT / src_name
    dest = SRC / dest_rel
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if DRY_RUN:
        print(f"[DRY] mv {src} -> {dest}")
        return
    if dest.exists():
        # merge: move contents in
        for p in src.rglob("*"):
            rel = p.relative_to(src)
            target = dest / rel
            if p.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(target))
        shutil.rmtree(src)
    else:
        shutil.move(str(src), str(dest))


def ensure_layout():
    (ROOT / "src").mkdir(exist_ok=True)
    (ROOT / "src" / "qaai").mkdir(parents=True, exist_ok=True)
    (ROOT / "configs").mkdir(exist_ok=True)
    (ROOT / "scripts").mkdir(exist_ok=True)


def move_configs():
    # unify config files
    pairs = [
        ("config/execution.yaml", "execution.yaml"),
        ("infra/config.yaml", "app.yaml"),
    ]
    for s, d in pairs:
        src = ROOT / s
        dest = ROOT / "configs" / d
        if src.exists():
            if DRY_RUN:
                print(f"[DRY] mv {src} -> {dest}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))


def move_root_scripts():
    # sweep run_*.py, *_orchestrator.py, scheduler.py into scripts/
    for p in ROOT.glob("*.py"):
        name = p.name
        if (
            name.startswith("run_")
            or name.endswith("_orchestrator.py")
            or name in {"scheduler.py", "main_orchestrator.py"}
        ):
            dest = ROOT / "scripts" / name
            if DRY_RUN:
                print(f"[DRY] mv {p} -> {dest}")
            else:
                shutil.move(str(p), str(dest))


def main():
    ensure_layout()
    for src_name, dest_rel in MAPS:
        move_dir(src_name, dest_rel)
    move_configs()
    move_root_scripts()
    print("\nDone. Review DRY output. Set DRY_RUN=False to apply.")


if __name__ == "__main__":
    main()
