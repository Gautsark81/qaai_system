from typing import Dict
from core.live_ops.screening import ScreeningResult


def score_screening_result(result: ScreeningResult) -> float:
    """
    Deterministic watchlist score.
    Bounded, stable, explainable.
    """
    base = result.score

    # Penalize failures deterministically
    penalty = 0.0
    for r in result.reasons:
        penalty += 0.05

    final = max(0.0, min(1.0, base - penalty))
    return round(final, 6)
