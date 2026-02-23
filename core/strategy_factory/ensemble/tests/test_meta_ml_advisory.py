from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)
from core.strategy_factory.ensemble.meta_alpha import MetaAlphaCalculator


def test_ml_advisory_delta_applied():
    strategies = [
        EnsembleStrategy("A", 95, 2),
    ]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        meta_ml_enabled=True,
    )

    result = EnsembleAllocator.allocate(snap)
    meta = MetaAlphaCalculator.calculate(snap, result)

    assert meta.scores["A"] > 0