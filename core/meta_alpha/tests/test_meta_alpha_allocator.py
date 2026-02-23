from dataclasses import dataclass
from typing import Tuple, Optional
from core.meta_alpha import MetaAlphaAllocator


@dataclass(frozen=True)
class StrategyIntelStub:
    strategy_id: str
    health: str              # HEALTHY | DEGRADING | UNSTABLE
    ssr: float
    promotion_signal: str    # PROMOTION_ELIGIBLE | NONE


def test_meta_alpha_allocates_to_healthy_strategies():
    intel = (
        StrategyIntelStub("S1", "HEALTHY", 0.92, "PROMOTION_ELIGIBLE"),
        StrategyIntelStub("S2", "HEALTHY", 0.88, "NONE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=0.6)

    result = allocator.allocate(
        strategies=intel,
        total_capital=1.0,
    )

    weights = {r.strategy_id: r.recommended_weight for r in result}

    assert weights["S1"] > 0
    assert weights["S2"] > 0
    assert sum(weights.values()) <= 1.0


def test_meta_alpha_blocks_unstable_strategies():
    intel = (
        StrategyIntelStub("S1", "UNSTABLE", 0.55, "NONE"),
        StrategyIntelStub("S2", "HEALTHY", 0.90, "PROMOTION_ELIGIBLE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=0.7)

    result = allocator.allocate(
        strategies=intel,
        total_capital=1.0,
    )

    weights = {r.strategy_id: r.recommended_weight for r in result}

    assert weights["S1"] == 0.0
    assert weights["S2"] > 0


def test_meta_alpha_caps_degrading_strategies():
    intel = (
        StrategyIntelStub("S1", "DEGRADING", 0.45, "NONE"),
        StrategyIntelStub("S2", "HEALTHY", 0.85, "PROMOTION_ELIGIBLE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=0.5)

    result = allocator.allocate(
        strategies=intel,
        total_capital=1.0,
    )

    weights = {r.strategy_id: r.recommended_weight for r in result}

    assert 0 < weights["S1"] <= 0.5
    assert weights["S2"] <= 0.5


def test_meta_alpha_enforces_max_cap():
    intel = (
        StrategyIntelStub("S1", "HEALTHY", 0.95, "PROMOTION_ELIGIBLE"),
        StrategyIntelStub("S2", "HEALTHY", 0.93, "PROMOTION_ELIGIBLE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=0.4)

    result = allocator.allocate(
        strategies=intel,
        total_capital=1.0,
    )

    for r in result:
        assert r.recommended_weight <= 0.4


def test_meta_alpha_is_deterministic():
    intel = (
        StrategyIntelStub("S1", "HEALTHY", 0.91, "PROMOTION_ELIGIBLE"),
        StrategyIntelStub("S2", "DEGRADING", 0.42, "NONE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=0.5)

    r1 = allocator.allocate(intel, total_capital=1.0)
    r2 = allocator.allocate(intel, total_capital=1.0)

    assert r1 == r2


def test_meta_alpha_provides_rationale():
    intel = (
        StrategyIntelStub("S1", "HEALTHY", 0.90, "PROMOTION_ELIGIBLE"),
    )

    allocator = MetaAlphaAllocator(max_per_strategy=1.0)

    result = allocator.allocate(
        strategies=intel,
        total_capital=1.0,
    )

    entry = result[0]

    assert isinstance(entry.rationale, str)
    assert "HEALTHY" in entry.rationale


def test_meta_alpha_has_no_side_effects():
    allocator = MetaAlphaAllocator(max_per_strategy=0.5)

    assert not hasattr(allocator, "execute")
    assert not hasattr(allocator, "place_order")
    assert not hasattr(allocator, "override_capital")
