# ml/feature_utils.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any

# compute feature dict (use ml/feature_utils.compute_basic_features_from_bars)
try:
    features = compute_features_for_symbol(sym, bars)  # implement or call ml.feature_utils
except Exception:
    features = None

ml_prob = 0.0
try:
    if getattr(self, "scorer", None) is not None:
        ml_prob = float(self.scorer.score(features))
except Exception:
    logger.exception("scorer.score failed")
# pass ml_prob to strategy context or use in meta-decision

def compute_basic_features_from_bars(bars: pd.DataFrame) -> Dict[str, float]:
    """
    Accept OHLCV bars DataFrame with index DatetimeIndex and columns
    ['open','high','low','close','volume'] and return a compact numeric dict.
    Typical features:
      - last_return: last close / open - 1
      - vwap: sum(price*vol)/sum(vol)
      - vol_1: volume of last bar
      - atr_5: average true range over 5 bars
      - volatility_10: std of returns over 10 bars
    """
    if bars is None or bars.empty:
        return {
            "last_return": 0.0,
            "vwap": 0.0,
            "vol_1": 0.0,
            "atr_5": 0.0,
            "volatility_10": 0.0,
        }

    close = bars["close"]
    last_idx = close.index[-1]
    last_close = float(close.iloc[-1])
    last_open = float(bars["open"].iloc[-1]) if "open" in bars.columns else last_close
    last_return = (last_close / last_open - 1.0) if last_open != 0 else 0.0

    # vwap
    if "volume" in bars.columns and bars["volume"].sum() > 0:
        vwap = float((bars["close"] * bars["volume"]).sum() / bars["volume"].sum())
    else:
        vwap = float(last_close)

    vol_1 = float(bars["volume"].iloc[-1]) if "volume" in bars.columns else 0.0

    # ATR over 5 bars
    high = bars["high"] if "high" in bars.columns else bars["close"]
    low = bars["low"] if "low" in bars.columns else bars["close"]
    tr = np.maximum(high - low, np.maximum(abs(high - bars["close"].shift(1).fillna(high)), abs(low - bars["close"].shift(1).fillna(low))))
    atr_5 = float(tr.tail(5).mean()) if len(tr) >= 1 else 0.0

    # volatility: std of returns over 10 bars
    returns = close.pct_change().fillna(0.0)
    vol10 = float(returns.tail(10).std()) if len(returns) >= 1 else 0.0

    return {
        "last_return": float(last_return),
        "vwap": float(vwap),
        "vol_1": float(vol_1),
        "atr_5": float(atr_5),
        "volatility_10": float(vol10),
    }
