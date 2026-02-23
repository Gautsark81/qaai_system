def compute_weight(snapshot) -> float:
    """
    Compute raw strategy capital weight ∈ [0, 1]
    """
    ssr_factor = min(max(snapshot.ssr, 0.0), 1.0)
    expectancy_factor = min(max(snapshot.expectancy, 0.0), 1.0)
    drawdown_factor = max(1.0 - snapshot.max_drawdown, 0.0)

    return round(
        ssr_factor * expectancy_factor * drawdown_factor,
        6,
    )
