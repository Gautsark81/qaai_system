# qaai_system/strategy_factory/fitness/fitness_evaluator.py

from __future__ import annotations
from typing import Dict

from .fitness_score import compute_fitness_score
from .promotion_rules import passes_backtest_thresholds


def evaluate_fitness(backtest_result: Dict) -> Dict:
    """
    Canonical fitness evaluation.

    Input:
        {
            "metrics": {
                "trades": int,
                "win_rate": float,
                "profit_factor": float,
                "max_drawdown": float,
                "sharpe": float,
            }
        }

    Output:
        metrics + fitness_score + passed
    """

    metrics = backtest_result["metrics"]

    fitness_score = compute_fitness_score(
        win_rate=float(metrics["win_rate"]),
        profit_factor=float(metrics["profit_factor"]),
        max_drawdown=float(metrics["max_drawdown"]),
        sharpe=float(metrics.get("sharpe", 0.0)),
    )

    passed = passes_backtest_thresholds(metrics)

    return {
        **metrics,
        "fitness_score": fitness_score,
        "passed": passed,
    }
