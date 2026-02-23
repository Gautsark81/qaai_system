# tests/phase_h/test_dry_run_blocks_orders.py

import pytest
import tempfile

from modules.order_manager.manager import OrderManager
from modules.order_manager.ledger import PlanLedger
from modules.execution.plan import ExecutionPlan
from modules.brokers.interface import Broker
from modules.runtime.testing import override_runtime_flags


class FakeBroker(Broker):
    def submit_market_order(self, **kwargs):
        raise AssertionError("Broker must not be called when trading is blocked")


def test_dry_run_blocks_order_submission():
    """
    Order submission must be blocked when runtime trading is disabled.
    Broker must never be called.
    """
    with override_runtime_flags(DRY_RUN=True):
        with tempfile.TemporaryDirectory() as d:
            ledger = PlanLedger(path=f"{d}/ledger.json")
            om = OrderManager(
                broker=FakeBroker(),
                ledger=ledger,
            )

            plan = ExecutionPlan(
                plan_id="PLAN-DRY-RUN",
                strategy_id="s1",
                symbol="NIFTY",
                side="BUY",
                quantity=1,
                order_type="MARKET",
                reason="test",
            )

            with pytest.raises(RuntimeError):
                om.submit(plan)
