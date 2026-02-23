"""
Strategy-level metrics aggregator.

Contract:
- Accepts iterable of Trade objects
- Trades must expose at minimum: net_r
- Optional helpers (avg_r(), expectancy(), etc.) are used if present
"""

from typing import Iterable


class StrategyAggregator:
    def aggregate(self, trades, risk_events, execution_stats):
        if not trades:
            return {
                "avg_r": 0.0,
                "expectancy": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "risk_blocks": 0,
                "atr_violations": 0,
                "position_size_violations": 0,
                "avg_slippage": 0.0,
                "p95_slippage": 0.0,
                "order_reject_rate": 0.0,
                "latency_p95_ms": 0.0,
            }

        r_vals = [t.net_r for t in trades]

        wins = [r for r in r_vals if r > 0]
        losses = [-r for r in r_vals if r < 0]

        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        for r in r_vals:
            equity += r
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)

        return {
            "avg_r": sum(r_vals) / len(r_vals),
            "expectancy": (
                (sum(wins) / len(wins)) if wins else 0.0
            ) - (
                (sum(losses) / len(losses)) if losses else 0.0
            ),
            "profit_factor": (sum(wins) / sum(losses)) if wins and losses else 0.0,
            "max_drawdown": max_dd,
            "risk_blocks": risk_events.count_blocks(),
            "atr_violations": risk_events.count_atr(),
            "position_size_violations": risk_events.count_size(),
            "avg_slippage": execution_stats.avg_slippage(),
            "p95_slippage": execution_stats.p95_slippage(),
            "order_reject_rate": execution_stats.reject_rate(),
            "latency_p95_ms": execution_stats.latency_p95(),
        }
