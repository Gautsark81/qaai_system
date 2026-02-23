from core.strategy_factory.ensemble.snapshot import EnsembleSnapshot
from core.strategy_factory.ensemble.models import EnsembleStrategy
from core.strategy_factory.ensemble.regime_stability import RegimeStabilityEngine


def test_regime_step_limit():

    snapshot = EnsembleSnapshot(
        strategies=[EnsembleStrategy("A", ssr=90, drawdown_pct=5)],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        regime_score=1.0,
        previous_regime_score=0.0,
        regime_max_step=0.2,
        regime_smoothing_alpha=1.0,
    )

    stable = RegimeStabilityEngine.stabilize(snapshot)

    assert stable.stable_regime_score == 0.2