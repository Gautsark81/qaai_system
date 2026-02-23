from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.admission import StrategyAdmissionGate


def test_admission_gate():

    snapshot = EnsembleSnapshot(
        strategies=[
            EnsembleStrategy("A", ssr=90, drawdown_pct=5)
        ],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
    )

    candidates = {
        "NEW_STRAT_1": 85,
        "NEW_STRAT_2": 70,  # below suspension threshold (80 default)
    }

    result = StrategyAdmissionGate.evaluate(snapshot, candidates)

    assert "NEW_STRAT_1" in result.approved
    assert "NEW_STRAT_2" in result.rejected
    assert result.snapshot_hash == snapshot.snapshot_hash