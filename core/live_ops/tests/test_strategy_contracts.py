from core.live_ops.strategy import StrategyCandidate
from core.live_ops.enums import StrategyStage


def test_strategy_candidate_contract():
    strat = StrategyCandidate(
        strategy_id="mean_reversion_v1",
        stage=StrategyStage.GENERATED,
        ssr=0.82,
        sharpe=1.6,
        max_drawdown=0.09,
    )

    assert strat.strategy_id
    assert strat.stage == StrategyStage.GENERATED
    assert 0.0 <= strat.ssr <= 1.0
    assert strat.max_drawdown >= 0.0
