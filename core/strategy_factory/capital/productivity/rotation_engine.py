# core/strategy_factory/capital/productivity/rotation_engine.py

from typing import Dict


def compute_rotation_multipliers(
    opportunity_gaps: Dict[str, float],
    rotation_sensitivity: float = 1.0,
) -> Dict[str, float]:
    """
    Returns advisory multiplier per strategy.
    1.0 = neutral
    <1.0 = capital reduction advisory
    """

    multipliers = {}

    for strategy, gap in opportunity_gaps.items():
        reduction = gap * rotation_sensitivity
        multiplier = max(0.5, 1.0 - reduction)
        multipliers[strategy] = round(multiplier, 6)

    return multipliers