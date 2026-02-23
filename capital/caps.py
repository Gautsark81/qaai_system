MAX_STRATEGY_CAP = 0.25  # 25% of allocatable capital


def apply_caps(weight: float) -> float:
    return min(weight, MAX_STRATEGY_CAP)
