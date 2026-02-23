# core/strategy_reputation/decay.py
from typing import List
import math
from core.strategy_reputation.performance_cycle import PerformanceCycle


def compute_decayed_score(
    cycles: List[PerformanceCycle],
    *,
    half_life_cycles: float,
) -> float:
    """
    Computes decayed average PnL using cycle-based half-life.
    """

    if not cycles:
        return 0.0

    weighted_sum = 0.0
    weight_total = 0.0

    for age, cycle in enumerate(reversed(cycles)):
        weight = math.exp(-math.log(2) * age / half_life_cycles)
        weighted_sum += cycle.pnl * weight
        weight_total += weight

    return round(weighted_sum / weight_total, 3)

# core/strategy_reputation/decay.py (continued)

def compute_decay_immunity_factor(cycle_count: int) -> float:
    """
    Immunity ∈ [0.5, 1.5]
    Increases monotonically with cycle count.
    """

    if cycle_count <= 1:
        return 0.5

    # Smooth saturation curve
    # Approaches 1.5 asymptotically
    growth = 1.0 - math.exp(-cycle_count / 5.0)

    immunity = 0.5 + growth  # → max 1.5
    return round(min(1.5, immunity), 3)


# core/strategy_reputation/decay.py (continued)

def compute_time_resilient_score(
    strategy_id: str,
    cycles: List[PerformanceCycle],
) -> float:
    """
    Computes PnL score with long-term decay immunity.
    """

    relevant = [c for c in cycles if c.strategy_id == strategy_id]
    if not relevant:
        return 0.0

    immunity = compute_decay_immunity_factor(len(relevant))

    # Base half-life is 3 cycles, extended by immunity
    half_life = 3.0 * immunity

    return compute_decayed_score(
        relevant,
        half_life_cycles=half_life,
    )

