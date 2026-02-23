from modules.strategy_tournament.backtest_executor import BacktestExecutor


def test_executor_has_required_methods():
    executor = BacktestExecutor(symbols=[], backtest_engine=None)
    assert hasattr(executor, "run_strategy")
    assert hasattr(executor, "run_all")
