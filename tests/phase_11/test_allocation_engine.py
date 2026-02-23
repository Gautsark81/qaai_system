import pytest

from model_ops.capital.allocation_engine import (
    AllocationEngine,
    AllocationInput,
)


def test_basic_weighted_allocation():
    engine = AllocationEngine()

    inp = AllocationInput(
        weights={
            "s1": 1.0,
            "s2": 1.0,
        },
        capital=100.0,
    )

    result = engine.allocate(inp)

    assert result.allocations["s1"] == pytest.approx(50.0)
    assert result.allocations["s2"] == pytest.approx(50.0)
    assert result.total_allocated == pytest.approx(100.0)


def test_zero_or_empty_inputs_produce_empty_allocation():
    engine = AllocationEngine()

    result = engine.allocate(
        AllocationInput(weights={}, capital=100.0)
    )

    assert result.allocations == {}
    assert result.total_allocated == 0.0


def test_negative_weights_are_rejected():
    engine = AllocationEngine()

    with pytest.raises(ValueError):
        engine.allocate(
            AllocationInput(
                weights={"s1": -1.0},
                capital=100.0,
            )
        )


def test_max_per_strategy_cap_enforced():
    engine = AllocationEngine(max_per_strategy_fraction=0.5)

    inp = AllocationInput(
        weights={
            "s1": 10.0,
            "s2": 1.0,
        },
        capital=100.0,
    )

    result = engine.allocate(inp)

    # s1 would have received ~90 without cap
    assert result.allocations["s1"] == pytest.approx(50.0)

    # s2 must not exceed remaining allocatable capital
    assert result.allocations["s2"] <= 50.0 + 1e-9

    # Capital conservation invariant
    assert result.total_allocated <= 100.0 + 1e-9


def test_allocation_is_deterministic():
    engine = AllocationEngine()

    inp = AllocationInput(
        weights={
            "a": 3.0,
            "b": 7.0,
        },
        capital=100.0,
    )

    r1 = engine.allocate(inp)
    r2 = engine.allocate(inp)

    assert r1.allocations == r2.allocations
    assert r1.total_allocated == r2.total_allocated
