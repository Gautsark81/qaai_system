import numpy as np
import pandas as pd
import time


def gen_ticks(
    symbol: str,
    start_ts: float | None = None,
    num_ticks: int = 1000,
    step_s: float = 1.0,
):
    if start_ts is None:
        start_ts = time.time()

    ticks = []
    price = 100.0
    for i in range(num_ticks):
        ticks.append(
            {
                "symbol": symbol,
                "timestamp": start_ts + i * step_s,
                "price": price + (i * 0.0002),
                "size": 1,
            }
        )
    return ticks


def naive_sma_signals(ticks, window: int):
    """
    Naive SMA (scalar).

    CONTRACT (from tests):
    - Accepts list[dict] OR pd.Series
    - Returns ONLY the last SMA value (float or NaN)
    """
    if isinstance(ticks, list):
        prices = pd.Series([t["price"] for t in ticks])
    else:
        prices = ticks

    if len(prices) < window:
        return np.nan

    return prices.iloc[-window:].mean()


def vectorized_sma_last(ticks, window: int):
    """
    Vectorized SMA (scalar).
    """
    if isinstance(ticks, list):
        prices = pd.Series([t["price"] for t in ticks])
    else:
        prices = ticks

    return prices.rolling(window).mean().iloc[-1]
