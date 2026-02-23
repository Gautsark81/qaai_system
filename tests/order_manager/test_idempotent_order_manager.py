# tests/order_manager/test_idempotent_order_manager.py

import tempfile
from dataclasses import dataclass

from modules.order_manager.manager import OrderManager
from modules.order_manager.ledger import PlanLedger
from modules.execution.plan import ExecutionPlan
from modules.brokers.interface import Broker


@dataclass
class FakeOrder:
    broker_order_id: str


class FakeBroker(Broker):
    def __init__(self):
        self.calls = 0

    def submit_market_order(self, *, symbol, side, quantity, client_order_id):
        self.calls += 1
        return FakeOrder(broker_order_id=f"BRK-{client_order_id}")


def make_plan():
    return ExecutionPlan(
        plan_id="PLAN-1",
        strategy_id="s1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        order_type="MARKET",
        reason="test",
    )


def test_exactly_once_submission_across_retries():
    with tempfile.TemporaryDirectory() as d:
        ledger = PlanLedger(path=f"{d}/ledger.json")
        broker = FakeBroker()
        om = OrderManager(broker=broker, ledger=ledger)

        plan = make_plan()

        oid1 = om.submit(plan)
        oid2 = om.submit(plan)

        assert oid1 == oid2
        assert broker.calls == 1


def test_restart_safety_ledger_persists():
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/ledger.json"

        broker = FakeBroker()
        ledger1 = PlanLedger(path=path)
        om1 = OrderManager(broker=broker, ledger=ledger1)

        plan = make_plan()
        oid1 = om1.submit(plan)

        # simulate restart
        ledger2 = PlanLedger(path=path)
        om2 = OrderManager(broker=broker, ledger=ledger2)

        oid2 = om2.submit(plan)

        assert oid1 == oid2
        assert broker.calls == 1
