# qaai_system/strategy_factory/backtesting/strategy_backtest_runner.py

from __future__ import annotations
from typing import Dict


class StrategyBacktestRunner:
    """
    Adapter around existing backtest engine.
    """

    def __init__(self, backtester):
        self.backtester = backtester

    def run(self, strategy_spec, window_months: int = 6) -> Dict:
        result = self.backtester.run(
            strategy=strategy_spec,
            lookback_months=window_months,
        )

        return {
            "strategy_id": strategy_spec.strategy_id,
            "metrics": result.metrics,
            "trades": result.trades,
        }
