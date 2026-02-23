# qaai_system/strategy_factory/fitness/promotion_rules.py

from __future__ import annotations


def passes_backtest_thresholds(metrics: dict) -> bool:
    return (
        metrics["trades"] >= 200
        and metrics["win_rate"] >= 0.80
        and metrics["profit_factor"] >= 1.40
        and metrics["max_drawdown"] <= 0.15
    )
