def score_strategy(snapshot) -> float:
    """
    Ranking score ONLY.
    Does not determine eligibility.
    """

    return round(
        0.40 * snapshot.ssr
        + 0.25 * snapshot.expectancy
        + 0.20 * snapshot.profit_factor
        - 0.15 * snapshot.max_drawdown,
        6,
    )
