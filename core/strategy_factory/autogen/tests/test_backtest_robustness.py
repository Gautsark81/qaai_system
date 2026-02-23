from core.strategy_factory.autogen.backtest_batch_runner import (
    DeterministicBacktestBatchRunner,
    BacktestMetrics,
)
from core.strategy_factory.autogen.candidate_registry import CandidateRegistry
from core.strategy_factory.autogen.hypothesis_models import StrategyHypothesis


def mock_backtest(h, symbol, window):
    return BacktestMetrics(
        ssr=85.0,
        max_drawdown=10.0,
        capital_efficiency=1.2,
    )


def test_robust_validation_passes():

    registry = CandidateRegistry()

    hypothesis = StrategyHypothesis(
        hypothesis_id="H1",
        version=1,
        feature_set={"momentum": 1.0},
        entry_logic="cross",
        exit_logic="fixed",
        timeframe="1h",
        regime_target="NEUTRAL",
    )

    registry.register_lab_candidate("H1", hypothesis.compute_hash())

    runner = DeterministicBacktestBatchRunner(
        registry=registry,
        backtest_callable=mock_backtest,
        watchlist=["A", "B"],
        windows=[("2020", "2021"), ("2021", "2022")],
    )

    result = runner.run(hypothesis)

    assert result is not None
    latest = registry.get_latest("H1")
    assert latest.stage.name == "ROBUST_VALIDATED"