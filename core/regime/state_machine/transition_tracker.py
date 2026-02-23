def compute_transition_score(
    vol_delta: float,
    corr_delta: float,
    breadth_delta: float,
) -> float:
    score = (
        0.5 * abs(vol_delta) +
        0.3 * abs(corr_delta) +
        0.2 * abs(breadth_delta)
    )
    return round(min(1.0, max(0.0, score)), 6)