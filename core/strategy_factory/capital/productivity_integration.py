# core/strategy_factory/capital/productivity_integration.py

from typing import List, Dict

from core.strategy_factory.capital.productivity.productivity_model import (
    ProductivitySnapshot,
)
from core.strategy_factory.capital.productivity.opportunity_cost_engine import (
    compute_opportunity_cost,
)
from core.strategy_factory.capital.productivity.rotation_engine import (
    compute_rotation_multipliers,
)


def compute_productivity_rotation_map(
    snapshots: List[ProductivitySnapshot],
    *,
    gap_threshold: float = 0.0,
    rotation_sensitivity: float = 1.0,
) -> Dict[str, float]:
    """
    Returns advisory productivity multiplier per strategy.

    Rules:
    - Best performer always 1.0
    - Underperformers reduced proportionally
    - Never increases capital above 1.0
    - Deterministic
    """

    if not snapshots:
        return {}

    gaps = compute_opportunity_cost(
        snapshots=snapshots,
        threshold=gap_threshold,
    )

    multipliers = compute_rotation_multipliers(
        opportunity_gaps=gaps,
        rotation_sensitivity=rotation_sensitivity,
    )

    # Enforce upper bound 1.0 (no amplification)
    for k in multipliers:
        multipliers[k] = min(1.0, multipliers[k])

    return multipliers