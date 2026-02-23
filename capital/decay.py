def apply_decay(weight: float, snapshot):
    """
    Apply SSR + drawdown based decay.
    Returns (new_weight, status, reason)
    """

    if snapshot.max_drawdown >= 1.0:
        return 0.0, "FROZEN", "MAX_DRAWDOWN_EXCEEDED"

    if snapshot.max_drawdown >= 0.75:
        return weight * 0.25, "THROTTLED", "SEVERE_DRAWDOWN"

    if snapshot.max_drawdown >= 0.50:
        return weight * 0.50, "THROTTLED", "MODERATE_DRAWDOWN"

    if snapshot.ssr < 0.70:
        return weight * 0.40, "THROTTLED", "LOW_SSR"

    if snapshot.ssr < 0.80:
        return weight * 0.70, "THROTTLED", "SSR_DECAY"

    return weight, "ACTIVE", None
