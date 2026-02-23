from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.regime_adjustment import RegimeAdjustmentEngine


def test_regime_adjustment():

    snapshot = EnsembleSnapshot(
        strategies=[EnsembleStrategy("A", ssr=90, drawdown_pct=5)],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        decay_penalty_strength=0.3,
        reinforcement_strength=0.1,
        regime_score=1.0,  # expansion
    )

    adjusted = RegimeAdjustmentEngine.adjust(snapshot)

    assert adjusted.adjusted_reinforcement_strength > snapshot.reinforcement_strength
    assert adjusted.adjusted_decay_strength <= snapshot.decay_penalty_strength
    assert adjusted.snapshot_hash == snapshot.snapshot_hash