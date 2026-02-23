from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.allocator import EnsembleAllocator
from core.strategy_factory.ensemble.retirement import StrategyRetirementEngine
from core.strategy_factory.ensemble.replacement import ReplacementQueueEngine


def test_replacement_queue_creation():

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
        suspension_min_ssr=60.0,
        decay_scores={"A": 0.8, "B": 0.1},
    )

    allocation = EnsembleAllocator.allocate(snapshot)
    retirement = StrategyRetirementEngine.evaluate(snapshot, allocation)

    queue = ReplacementQueueEngine.build(snapshot, retirement)

    assert queue.replacement_slots == ["A"]