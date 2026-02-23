from core.strategy_factory.capital.productivity.rotation_engine import (
    compute_rotation_multipliers,
)


def test_rotation_reduces_underperformer():
    gaps = {"A": 0.0, "B": 0.1}

    multipliers = compute_rotation_multipliers(gaps)

    assert multipliers["A"] == 1.0
    assert multipliers["B"] < 1.0