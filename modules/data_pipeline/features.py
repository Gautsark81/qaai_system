import pandas as pd
import numpy as np

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period, min_periods=1).mean()
    return atr

def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    close = df["close"].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.rolling(period, min_periods=1).mean()
    avg_loss = loss.rolling(period, min_periods=1).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def compute_ema(df: pd.DataFrame, span: int) -> pd.Series:
    return df["close"].ewm(span=span, adjust=False).mean()

def compute_realized_vol(df: pd.DataFrame, window: int = 21) -> pd.Series:
    ret = df["close"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return ret.rolling(window, min_periods=1).std() * (252 ** 0.5)

def compute_liquidity_value(df: pd.DataFrame, window: int = 21) -> pd.Series:
    return (df["close"] * df["volume"]).rolling(window, min_periods=1).mean()

def compute_rolling_features(df: pd.DataFrame, window_days: int = 21) -> pd.DataFrame:
    df = df.sort_index().copy()
    if df.empty:
        return df
    res = pd.DataFrame(index=df.index)
    res["close"] = df["close"]
    res["volume"] = df["volume"]
    res["atr_14"] = compute_atr(df, period=14)
    res["rsi_14"] = compute_rsi(df, period=14)
    res["ema_10"] = compute_ema(df, span=10)
    res["ema_50"] = compute_ema(df, span=50)
    res["ema_slope_10"] = res["ema_10"].pct_change(5).fillna(0.0)
    res["ema_slope_50"] = res["ema_50"].pct_change(5).fillna(0.0)
    res["realized_vol_21"] = compute_realized_vol(df, window=window_days)
    res["liquidity_value_21"] = compute_liquidity_value(df, window=window_days)
    return res
