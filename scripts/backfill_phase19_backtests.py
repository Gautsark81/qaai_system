from intelligence.backtest_adapter import BacktestIntelligenceAdapter
from backtests.repository import BacktestRepository

adapter = BacktestIntelligenceAdapter()
repo = BacktestRepository()

for bt in repo.load_all_completed():
    adapter.process_backtest(
        strategy_id=bt.strategy_id,
        strategy_version=bt.strategy_version,
        trades=bt.trades,
        risk_events=bt.risk_events,
        execution_stats=bt.execution_stats,
        window_start=bt.start,
        window_end=bt.end,
    )
