# core/strategy_factory/capital/productivity/opportunity_cost_engine.py

from typing import List
from .productivity_model import ProductivitySnapshot


def compute_opportunity_cost(
    snapshots: List[ProductivitySnapshot],
    threshold: float = 0.02,
) -> dict:
    """
    Returns mapping of strategy_dna → opportunity_gap
    Positive gap means capital could be better deployed elsewhere.
    """

    if not snapshots:
        return {}

    best_eff = max(
        s.regime_adjusted_efficiency for s in snapshots
    )

    gaps = {}

    for s in snapshots:
        gap = best_eff - s.regime_adjusted_efficiency
        gaps[s.strategy_dna] = round(gap, 6)

    return gaps