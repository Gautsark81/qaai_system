from __future__ import annotations

# qaai_system/signal_engine/selector_utils.py
import pandas as pd
import numpy as np


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate technical features for a given OHLCV dataframe.
    Output: ['returns', 'ma_ratio', 'rsi', 'atr', 'bbw']
    """
    expected_cols = ["returns", "ma_ratio", "rsi", "atr", "bbw"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected_cols)

    out = pd.DataFrame(index=df.index)

    out["returns"] = df["close"].pct_change().fillna(0.0)

    ma_short = df["close"].rolling(window=5, min_periods=1).mean()
    ma_long = df["close"].rolling(window=20, min_periods=1).mean().replace(0, np.nan)
    out["ma_ratio"] = (ma_short / ma_long).fillna(1.0)

    out["rsi"] = _rsi(df["close"], period=14)

    if all(c in df.columns for c in ("high", "low", "close")):
        out["atr"] = _atr(df, period=14)
    else:
        out["atr"] = pd.Series(0.0, index=df.index)

    out["bbw"] = _bollinger_bandwidth(df["close"], window=20, num_std=2.0)

    return out.reindex(df.index).fillna(0.0)[expected_cols]


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff().fillna(0.0)
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return (100.0 - (100.0 / (1.0 + rs))).fillna(50.0)


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1).fillna(df["close"])
    tr1 = (df["high"] - df["low"]).abs()
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean().fillna(0.0)


def _bollinger_bandwidth(
    series: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.Series:
    mid = series.rolling(window=window, min_periods=1).mean()
    std = series.rolling(window=window, min_periods=1).std().fillna(0.0)
    width = 2.0 * num_std * std
    return (width / mid.replace(0.0, np.nan)).fillna(0.0)
