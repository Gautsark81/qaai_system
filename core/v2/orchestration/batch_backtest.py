# core/v2/orchestration/batch_backtest.py
from typing import List
from .contracts import StrategyCandidate, BacktestResult


class BatchBacktester:
    """
    Pure simulation layer.
    Deterministic mock logic (replaceable later).
    """

    def run(self, candidates: List[StrategyCandidate]) -> List[BacktestResult]:
        results: List[BacktestResult] = []

        for c in candidates:
            results.append(
                BacktestResult(
                    strategy_id=c.strategy_id,
                    ssr=0.6 + (hash(c.strategy_id) % 20) / 100,
                    pnl=1000.0,
                    drawdown=200.0,
                    trades=50,
                )
            )

        return results
