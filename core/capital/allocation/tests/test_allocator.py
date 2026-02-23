# core/capital/allocation/tests/test_allocator.py

from core.capital.allocation.allocator import (
    PortfolioCapitalAllocator,
    StrategyCapitalSignal,
)


def test_weights_sum_to_one():
    allocator = PortfolioCapitalAllocator()

    weights = allocator.allocate(
        signals={
            "A": StrategyCapitalSignal(0.8, 0.9, 1.0),
            "B": StrategyCapitalSignal(0.6, 0.8, 0.5),
        }
    )

    assert round(sum(weights.values()), 6) == 1.0


def test_higher_quality_strategy_gets_more_weight():
    allocator = PortfolioCapitalAllocator()

    weights = allocator.allocate(
        signals={
            "GOOD": StrategyCapitalSignal(0.9, 0.9, 1.0),
            "BAD": StrategyCapitalSignal(0.2, 0.3, 0.5),
        }
    )

    assert weights["GOOD"] > weights["BAD"]


def test_all_zero_inputs_return_zero_weights():
    allocator = PortfolioCapitalAllocator()

    weights = allocator.allocate(
        signals={
            "A": StrategyCapitalSignal(0.0, 0.0, 0.0),
            "B": StrategyCapitalSignal(0.0, 0.0, 0.0),
        }
    )

    assert weights == {"A": 0.0, "B": 0.0}


def test_min_weight_floor_is_respected():
    allocator = PortfolioCapitalAllocator()

    weights = allocator.allocate(
        signals={
            "A": StrategyCapitalSignal(1.0, 1.0, 1.0),
            "B": StrategyCapitalSignal(0.01, 0.01, 0.01),
        },
        min_weight=0.1,
    )

    assert weights["B"] >= 0.1
    assert round(sum(weights.values()), 6) == 1.0
