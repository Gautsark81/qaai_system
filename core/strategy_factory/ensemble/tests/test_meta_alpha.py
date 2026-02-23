from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)
from core.strategy_factory.ensemble.meta_alpha import (
    MetaAlphaCalculator,
)


def test_meta_score_computation():
    strategies = [
        EnsembleStrategy("A", 90, 5),
        EnsembleStrategy("B", 85, 10),
    ]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
    )

    result = EnsembleAllocator.allocate(snap)

    meta = MetaAlphaCalculator.calculate(snap, result)

    assert "A" in meta.scores
    assert "B" in meta.scores

    assert meta.scores["A"] > 0
    assert meta.scores["B"] > 0