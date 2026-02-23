from core.strategy_factory.capital.productivity.productivity_model import (
    compute_productivity_snapshot,
)
from core.strategy_factory.capital.productivity.opportunity_cost_engine import (
    compute_opportunity_cost,
)


def test_opportunity_gap():
    s1 = compute_productivity_snapshot(
        strategy_dna="A",
        net_return=100,
        avg_allocated_capital=1000,
        max_drawdown=0,
        regime_confidence=1.0,
    )

    s2 = compute_productivity_snapshot(
        strategy_dna="B",
        net_return=50,
        avg_allocated_capital=1000,
        max_drawdown=0,
        regime_confidence=1.0,
    )

    gaps = compute_opportunity_cost([s1, s2])

    assert gaps["A"] == 0.0
    assert gaps["B"] > 0