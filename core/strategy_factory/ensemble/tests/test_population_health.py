from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.allocator import EnsembleAllocator
from core.strategy_factory.ensemble.retirement import StrategyRetirementEngine
from core.strategy_factory.ensemble.replacement import ReplacementQueueEngine
from core.strategy_factory.ensemble.population_health import PopulationHealthEngine


def test_population_health_metrics():

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
        decay_scores={"A": 0.8, "B": 0.2},
    )

    allocation = EnsembleAllocator.allocate(snapshot)
    retirement = StrategyRetirementEngine.evaluate(snapshot, allocation)
    replacement = ReplacementQueueEngine.build(snapshot, retirement)

    health = PopulationHealthEngine.evaluate(
        snapshot,
        allocation,
        retirement,
        replacement,
    )

    assert health.active_count == 2
    assert health.suspended_count == 0
    assert health.retirement_candidates == 1
    assert health.replacement_slots == 1
    assert 0.0 <= health.stability_score <= 1.0
    assert health.snapshot_hash == snapshot.snapshot_hash