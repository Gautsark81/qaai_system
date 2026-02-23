from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.allocator import EnsembleAllocator
from core.strategy_factory.ensemble.retirement import StrategyRetirementEngine


def test_retirement_trigger():

    strategies = [
        EnsembleStrategy("A", ssr=70, drawdown_pct=5),
        EnsembleStrategy("B", ssr=90, drawdown_pct=5),
    ]

    snapshot = EnsembleSnapshot(
        strategies=strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,

        # ↓ IMPORTANT FIX
        suspension_min_ssr=60.0,  # allow A to remain active

        decay_scores={
            "A": 0.8,  # high decay
            "B": 0.1,
        },
    )

    allocation = EnsembleAllocator.allocate(snapshot)
    result = StrategyRetirementEngine.evaluate(snapshot, allocation)

    assert "A" in result.retirement_candidates
    assert "B" not in result.retirement_candidates