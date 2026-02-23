from core.strategy_factory.capital.productivity.productivity_model import (
    compute_productivity_snapshot,
)
from core.strategy_factory.capital.productivity_integration import (
    compute_productivity_rotation_map,
)


def test_rotation_map_basic_behavior():
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

    rotation_map = compute_productivity_rotation_map([s1, s2])

    assert rotation_map["A"] == 1.0
    assert rotation_map["B"] < 1.0


def test_rotation_never_amplifies():
    s1 = compute_productivity_snapshot(
        strategy_dna="A",
        net_return=100,
        avg_allocated_capital=1000,
        max_drawdown=0,
        regime_confidence=1.0,
    )

    rotation_map = compute_productivity_rotation_map([s1])

    assert rotation_map["A"] == 1.0