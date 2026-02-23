from core.capital.execution.slippage_gate import (
    SlippageGate,
    SlippageModel,
    OrderIntent,
)
from core.capital.result import CapitalAllocationResult


def test_order_blocked_when_slippage_exceeds_capital():
    gate = SlippageGate()

    allocation = CapitalAllocationResult(
        strategy_id="s1",
        allocated_capital=10_000.0,
        rationale=["cap"],
    )

    order = OrderIntent(
        symbol="NIFTY",
        price=100.0,
        quantity=100,  # base cost = 10,000
    )

    slippage = SlippageModel(max_slippage_pct=0.05)  # +5%

    result = gate.evaluate(
        allocation=allocation,
        order=order,
        slippage=slippage,
    )

    assert result.allowed is False
    assert "SLIPPAGE" in result.reason


def test_order_passes_when_within_slippage_cap():
    gate = SlippageGate()

    allocation = CapitalAllocationResult(
        strategy_id="s2",
        allocated_capital=12_000.0,
        rationale=["cap"],
    )

    order = OrderIntent(
        symbol="BANKNIFTY",
        price=100.0,
        quantity=100,
    )

    slippage = SlippageModel(max_slippage_pct=0.05)

    result = gate.evaluate(
        allocation=allocation,
        order=order,
        slippage=slippage,
    )

    assert result.allowed is True
    assert "PASSED" in result.reason


def test_zero_slippage_behaves_as_exact_cap():
    gate = SlippageGate()

    allocation = CapitalAllocationResult(
        strategy_id="s3",
        allocated_capital=10_000.0,
        rationale=["exact"],
    )

    order = OrderIntent(
        symbol="FINNIFTY",
        price=100.0,
        quantity=100,
    )

    slippage = SlippageModel(max_slippage_pct=0.0)

    result = gate.evaluate(
        allocation=allocation,
        order=order,
        slippage=slippage,
    )

    assert result.allowed is True
