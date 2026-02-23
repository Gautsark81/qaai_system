# scripts/run_deterministic_paper.py

import sys
from pathlib import Path
import shutil

# -------------------------------------------------
# Ensure project root is on PYTHONPATH
# -------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import boot_system
from core.paper.paper_executor import PaperExecutor


def clean():
    shutil.rmtree(ROOT / "data" / "paper", ignore_errors=True)


def run(run_id: str):
    executor = PaperExecutor(deterministic=True)

    # Boot system (deterministic context already enforced)
    boot_system()

    # Deterministic trade (placeholder for STEP-8 validation)
    executor.execute(
        strategy_id="STRAT_TEST",
        symbol="RELIANCE",
        side="BUY",
        qty=10,
        price=2500,
    )

    executor.ledger.flush(run_id)


if __name__ == "__main__":
    clean()
    run("A")
    run("B")
