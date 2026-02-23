from __future__ import annotations

from typing import Dict, Optional

from screening.context import ScreeningContext


def _safe_change(p_now: Optional[float], p_prev: Optional[float]) -> float:
    if p_now is None or p_prev is None or p_prev == 0:
        return 0.0
    return (p_now - p_prev) / p_prev


def compute_intraday_factors(ctx: ScreeningContext, symbol: str) -> Dict[str, float]:
    """
    Compute a basic intraday factor set for a symbol based on OHLCV + features.

    Supercharged:
    - Momentum (close-to-close)
    - Volatility proxy (high-low range)
    - Liquidity proxy (volume)
    - Optional extension hooks via FeatureStore (e.g. EMA, RSI, etc.)
    """
    tf = ctx.timeframe
    bars = ctx.ohlcv_store.get_bars(symbol, tf, limit=10)
    if not bars:
        return {}

    latest = bars[-1]
    prev = bars[-2] if len(bars) >= 2 else None

    mom_close = _safe_change(latest.close, prev.close if prev else None)
    intraday_range = (
        (latest.high - latest.low) / latest.close if latest.close else 0.0
    )
    vol = float(latest.volume or 0.0)

    # normalise/log-ish transforms for stability
    liquidity_score = vol ** 0.5 if vol > 0 else 0.0

    factors: Dict[str, float] = {
        "mom_close": float(mom_close),
        "range": float(intraday_range),
        "liquidity": float(liquidity_score),
    }

    # Hybrid: pull any extra computed features from FeatureStore if available
    fv = ctx.feature_store.latest(symbol, tf)
    if fv is not None:
        for name, val in fv.values.items():
            # keep only numeric features
            try:
                factors[name] = float(val)
            except Exception:
                continue

    return factors


def score_factors_linear(factors: Dict[str, float]) -> float:
    """
    Simple linear scoring function.

    You can later replace this with a learned model; for now weights are tuned
    by hand as a placeholder.
    """
    if not factors:
        return 0.0

    # basic weights; positive momentum, negative huge range (risk), positive liquidity
    w_mom = 2.0
    w_range = -1.0
    w_liq = 0.5

    score = 0.0
    mom = factors.get("mom_close", 0.0)
    rng = factors.get("range", 0.0)
    liq = factors.get("liquidity", 0.0)

    score += w_mom * mom
    score += w_range * rng
    score += w_liq * liq

    return float(score)
