from core.strategy_factory.autogen.backtest_batch_runner import (
    DeterministicBacktestBatchRunner,
    BacktestMetrics,
)
from core.strategy_factory.autogen.candidate_registry import CandidateRegistry
from core.strategy_factory.autogen.hypothesis_models import StrategyHypothesis


def mock_backtest(hypothesis, symbol):
    # deterministic mock
    return BacktestMetrics(
        ssr=85.0,
        max_drawdown=10.0,
        capital_efficiency=1.2,
    )


def test_backtest_updates_registry():

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
        watchlist=["A", "B", "C"],
    )

    result = runner.run(hypothesis)

    assert result is not None
    latest = registry.get_latest("H1")
    assert latest.stage.name == "BACKTESTED"


def test_ssr_filter_blocks_low_scores():

    registry = CandidateRegistry()

    hypothesis = StrategyHypothesis(
        hypothesis_id="H2",
        version=1,
        feature_set={"momentum": 1.0},
        entry_logic="cross",
        exit_logic="fixed",
        timeframe="1h",
        regime_target="NEUTRAL",
    )

    registry.register_lab_candidate("H2", hypothesis.compute_hash())

    def low_ssr_mock(h, s):
        return BacktestMetrics(
            ssr=60.0,
            max_drawdown=15.0,
            capital_efficiency=0.8,
        )

    runner = DeterministicBacktestBatchRunner(
        registry=registry,
        backtest_callable=low_ssr_mock,
        watchlist=["A", "B"],
    )

    result = runner.run(hypothesis)

    assert result is None
    latest = registry.get_latest("H2")
    assert latest.stage.name == "LAB"