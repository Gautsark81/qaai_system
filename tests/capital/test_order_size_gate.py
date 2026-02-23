from core.capital.enforcement.order_size_gate import OrderSizeGate
from core.capital.result import CapitalAllocationResult


def test_order_size_capped_by_capital():
    gate = OrderSizeGate()

    allocation = CapitalAllocationResult(
        strategy_id="s1",
        allocated_capital=5000.0,
        rationale=["limit"],
    )

    decision = gate.enforce(
        strategy_id="s1",
        requested_qty=10,
        max_allowed_qty=4,
        allocation=allocation,
    )

    assert decision.approved_qty == 4
    assert decision.requested_qty == 10
    assert decision.reason == "CAPITAL_CAPPED"


def test_order_size_passes_when_within_cap():
    gate = OrderSizeGate()

    allocation = CapitalAllocationResult(
        strategy_id="s1",
        allocated_capital=5000.0,
        rationale=["ok"],
    )

    decision = gate.enforce(
        strategy_id="s1",
        requested_qty=3,
        max_allowed_qty=5,
        allocation=allocation,
    )

    assert decision.approved_qty == 3
    assert decision.reason == "CAPITAL_APPROVED"
