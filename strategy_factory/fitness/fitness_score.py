# qaai_system/strategy_factory/fitness/fitness_score.py

from __future__ import annotations

def compute_fitness_score(
    *,
    win_rate: float,
    profit_factor: float,
    max_drawdown: float,
    sharpe: float,
) -> float:
    """
    Deterministic fitness scalar ∈ [0, 1].

    Stability > returns > risk-adjusted performance.
    """

    score = 0.0

    score += min(win_rate / 0.85, 1.0) * 0.35
    score += min(profit_factor / 2.0, 1.0) * 0.30
    score += min(sharpe / 2.5, 1.0) * 0.20
    score += max(0.0, 1.0 - max_drawdown / 0.25) * 0.15

    return round(min(score, 1.0), 4)
