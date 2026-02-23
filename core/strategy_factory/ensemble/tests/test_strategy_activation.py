from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.replacement import ReplacementQueueResult
from core.strategy_factory.ensemble.admission import AdmissionResult
from core.strategy_factory.ensemble.activation import StrategyActivationEngine


def test_activation_respects_slot_limit():

    snapshot = EnsembleSnapshot(
        strategies=[
            EnsembleStrategy("A", ssr=90, drawdown_pct=5)
        ],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
    )

    replacement = ReplacementQueueResult(
        replacement_slots=["OLD_STRAT"],
        snapshot_hash=snapshot.snapshot_hash,
    )

    admission = AdmissionResult(
        approved=["NEW_1", "NEW_2"],
        rejected={},
        snapshot_hash=snapshot.snapshot_hash,
    )

    result = StrategyActivationEngine.activate(
        snapshot,
        replacement,
        admission,
    )

    assert result.activated == ["NEW_1"]
    assert result.skipped == ["NEW_2"]
    assert result.snapshot_hash == snapshot.snapshot_hash