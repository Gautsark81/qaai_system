from core.strategy_factory.capital.productivity.productivity_model import (
    compute_productivity_snapshot,
)


def test_basic_efficiency():
    snap = compute_productivity_snapshot(
        strategy_dna="S1",
        net_return=100,
        avg_allocated_capital=1000,
        max_drawdown=-50,
        regime_confidence=1.0,
    )

    assert snap.capital_efficiency == 0.1
    assert snap.risk_adjusted_efficiency == 0.05
    assert snap.regime_adjusted_efficiency == 0.05