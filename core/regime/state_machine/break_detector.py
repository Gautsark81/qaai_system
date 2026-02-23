def compute_break_score(
    vol_extreme_flag: int,
    rapid_flip_flag: int,
    liquidity_flag: int,
) -> float:
    score = (
        0.6 * vol_extreme_flag +
        0.3 * rapid_flip_flag +
        0.1 * liquidity_flag
    )
    return round(min(1.0, max(0.0, score)), 6)