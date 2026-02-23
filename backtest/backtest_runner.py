"""
Backtest Runner
----------------
Executes backtests and emits Phase-19 Strategy Intelligence snapshots.

This file is the ONLY integration point between backtesting
and intelligence. Backtester logic remains untouched.
"""

from datetime import datetime
from backtester.backtester import Backtester
from intelligence.backtest_adapter import BacktestIntelligenceAdapter


class BacktestRunner:
    """
    Orchestrates a backtest run and wires Phase-19 post-run intelligence.
    """

    def __init__(self):
        self.backtester = Backtester()
        self.intelligence = BacktestIntelligenceAdapter()

    def run(
        self,
        *,
        strategy,
        start: datetime,
        end: datetime,
        capital: float,
    ):
        """
        Run backtest and generate Strategy Intelligence snapshot.
        """

        # 1️⃣ Run backtest (existing, deterministic logic)
        result = self.backtester.run(
            strategy=strategy,
            start=start,
            end=end,
            capital=capital,
        )

        # 2️⃣ Phase-19 Intelligence (POST backtest, read-only)
        self.intelligence.process_backtest(
            strategy_id=strategy.strategy_id,
            strategy_version=strategy.version,
            trades=result.trades,
            risk_events=result.risk_events,
            execution_stats=result.execution_stats,
            window_start=start,
            window_end=end,
        )

        # 3️⃣ Return original backtest result (no mutation)
        return result
