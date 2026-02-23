def compute_volatility_ratio(realized_vol: float, long_run_vol: float) -> float:
    if long_run_vol <= 0:
        return float("inf")
    return realized_vol / long_run_vol
