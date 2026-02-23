# backtester/fast_ohlcv.py
from __future__ import annotations
import numpy as np
import pandas as pd

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except Exception:
    NUMBA_AVAILABLE = False

def _group_by_int_seconds_numpy(ts_seconds: np.ndarray, prices: np.ndarray, sizes: np.ndarray, timeframe: int = 1):
    """
    Fast numpy grouping by integer second bins.
    Returns a DataFrame with open, high, low, close, volume indexed by bin timestamp.
    """
    # compute bin ids
    bins = (ts_seconds // timeframe).astype(np.int64)
    unique_bins, inverse_idx = np.unique(bins, return_inverse=True)
    opens = np.full(len(unique_bins), np.nan, dtype=float)
    highs = np.full(len(unique_bins), -np.inf, dtype=float)
    lows = np.full(len(unique_bins), np.inf, dtype=float)
    closes = np.full(len(unique_bins), np.nan, dtype=float)
    vols = np.zeros(len(unique_bins), dtype=float)

    # iterate and aggregate
    for i, b in enumerate(inverse_idx):
        p = prices[i]
        s = sizes[i]
        if np.isnan(opens[b]):
            opens[b] = p
        highs[b] = max(highs[b], p)
        lows[b] = min(lows[b], p)
        closes[b] = p
        vols[b] += s

    # drop bins with nan opens (no data)
    mask = ~np.isnan(opens)
    if not mask.any():
        return pd.DataFrame(columns=["open","high","low","close","volume"])
    idx = pd.to_datetime(unique_bins[mask].astype("int64"), unit="s")
    df = pd.DataFrame({
        "open": opens[mask],
        "high": highs[mask],
        "low": lows[mask],
        "close": closes[mask],
        "volume": vols[mask],
    }, index=idx)
    return df

def ohlcv_from_ticks_fast(ticks: list, timeframe_seconds: int = 1):
    """
    ticks: list of dicts with keys: 'timestamp' (float unix seconds), 'price' (float), 'size' (float/int)
    returns pandas DataFrame of OHLCV per timeframe_seconds bin
    """
    if not ticks:
        return pd.DataFrame(columns=["open","high","low","close","volume"])
    # convert to numpy
    ts = np.array([int(t["timestamp"]) for t in ticks], dtype=np.int64)
    prices = np.array([float(t["price"]) for t in ticks], dtype=float)
    sizes = np.array([float(t.get("size", 1.0)) for t in ticks], dtype=float)
    return _group_by_int_seconds_numpy(ts, prices, sizes, timeframe_seconds)
