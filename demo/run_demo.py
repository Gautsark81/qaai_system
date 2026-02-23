# demo/run_demo.py

import sys
from pathlib import Path

# ------------------------------------------------------------
# Bootstrap project root so `modules` and `demo` are importable
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ------------------------------------------------------------
# Imports (now guaranteed to work)
# ------------------------------------------------------------
from modules.runtime.testing import override_runtime_flags
from modules.order_manager.manager import OrderManager
from modules.order_manager.ledger import PlanLedger
from modules.execution.plan_builder import build_execution_plan_legacy

from demo.demo_strategy import DemoStrategy
from demo.fake_broker import FakeBroker


def main():
    with override_runtime_flags(
        DRY_RUN=True,
        AUDIT_ENABLED=True,
        METRICS_ENABLED=True,
    ):
        print("\n=== QAAI SYSTEM — DRY-RUN DEMO START ===\n")

        # 1️⃣ Strategy
        strategy = DemoStrategy(
            strategy_id="demo_strategy",
            version="1.0",
            symbol="NIFTY",
            timeframe="5m",
            params={},
        )

        intent = strategy.run({"price": 200})
        print("Intent:", intent)

        # 2️⃣ Plan
        plan = build_execution_plan_legacy(
            intent=intent,
            max_quantity=1,
        )
        print("\nExecution Plan:", plan)

        # 3️⃣ OrderManager (blocked by DRY_RUN)
        ledger = PlanLedger(path="state/demo_ledger.json")
        om = OrderManager(
            broker=FakeBroker(),
            ledger=ledger,
        )

        print("\nSubmitting order (should be blocked)...")
        try:
            om.submit(plan)
        except RuntimeError as e:
            print("Blocked as expected:", e)

        print("\n=== QAAI SYSTEM — DEMO COMPLETE ===\n")


if __name__ == "__main__":
    main()
