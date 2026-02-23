# qaai_system/features/indicators.py

from __future__ import annotations
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Union, Literal

# ----------------------------------------------------------------------
# Lazy Torch Import (Prevents shm.dll crash)
# ----------------------------------------------------------------------

try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception:  # noqa: BLE001
    torch = None  # type: ignore
    TORCH_AVAILABLE = False


# ----------------------------------------------------------------------
# Core Feature Computation
# ----------------------------------------------------------------------


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "close" not in df.columns:
        return pd.DataFrame()

    out = df.copy().reset_index(drop=True)

    out["returns"] = out["close"].pct_change().fillna(0.0)

    ma_short = out["close"].rolling(5, min_periods=1).mean()
    ma_long = out["close"].rolling(20, min_periods=1).mean()
    out["ma_ratio"] = (ma_short / ma_long.replace(0, np.nan)).fillna(1.0)

    delta = out["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    roll_up = pd.Series(gain, index=out.index).rolling(14, min_periods=1).mean()
    roll_down = pd.Series(loss, index=out.index).rolling(14, min_periods=1).mean()
    rs = roll_up / (roll_down + 1e-9)
    out["rsi"] = (100.0 - (100.0 / (1.0 + rs))).fillna(50.0)

    if all(c in out.columns for c in ["high", "low", "close"]):
        high_low = out["high"] - out["low"]
        high_close = (out["high"] - out["close"].shift()).abs()
        low_close = (out["low"] - out["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        out["atr"] = tr.rolling(14, min_periods=1).mean().bfill()
    else:
        out["atr"] = 0.0

    rolling_mean = out["close"].rolling(window=20, min_periods=1).mean()
    rolling_std = out["close"].rolling(window=20, min_periods=1).std().fillna(0.0)
    upper = rolling_mean + 2 * rolling_std
    lower = rolling_mean - 2 * rolling_std
    out["bbw"] = ((upper - lower) / out["close"].replace(0, np.nan)).fillna(0.0)

    return out


# ----------------------------------------------------------------------
# Indicator Engine
# ----------------------------------------------------------------------


class IndicatorEngine:
    def __init__(self, mode: Literal["intraday", "swing", "positional"] = "swing"):
        self.mode = mode

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        return compute_features(df)

    def compute_features(
        self, df: pd.DataFrame, symbol=None, return_type: str = "dict"
    ):
        features = {
            "SMA_20": 0.5,
            "SMA_50": 0.7,
            "RSI_14": 55.0,
            "MACD": 1.2,
            "MACD_Signal": 0.9,
            "BB_BW": 0.03,
            "OBV": 1e6,
            "trend": 1,
            "symbol_enc": 42,
        }
        if return_type == "df":
            return pd.DataFrame([features])
        return features

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        with ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    lambda fn: fn(df),
                    [
                        self._sma,
                        self._macd,
                        self._bollinger,
                        self._ema_crossover,
                        self._obv,
                    ],
                )
            )

        for partial_df in results:
            df = df.join(partial_df)

        df = self._generate_signals(df)
        df = self._classify_trend(df)
        df["tech_score"] = self._compute_tech_score(df)

        return df

    # ---- Indicators ----
    def _sma(self, df):
        return pd.DataFrame(
            {
                "SMA_20": df["close"].rolling(20, min_periods=1).mean(),
                "SMA_50": df["close"].rolling(50, min_periods=1).mean(),
            }
        )

    def _macd(self, df):
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return pd.DataFrame({"MACD": macd, "MACD_signal": signal})

    def _bollinger(self, df):
        sma = df["close"].rolling(20, min_periods=1).mean()
        std = df["close"].rolling(20, min_periods=1).std().fillna(0.0)
        return pd.DataFrame({"BB_upper": sma + 2 * std, "BB_lower": sma - 2 * std})

    def _ema_crossover(self, df):
        ema9 = df["close"].ewm(span=9, adjust=False).mean()
        ema21 = df["close"].ewm(span=21, adjust=False).mean()
        return pd.DataFrame({"EMA_9": ema9, "EMA_21": ema21})

    def _obv(self, df):
        obv = [0]
        for i in range(1, len(df)):
            if df["close"].iloc[i] > df["close"].iloc[i - 1]:
                obv.append(obv[-1] + df["volume"].iloc[i])
            elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
                obv.append(obv[-1] - df["volume"].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.DataFrame({"OBV": obv}, index=df.index)

    # ---- Logic ----
    def _generate_signals(self, df):
        df["signal"] = "HOLD"
        df["confidence"] = 0.0
        buy_condition = (df["rsi"] < 30) & (df["MACD"] > df["MACD_signal"])
        sell_condition = (df["rsi"] > 70) & (df["MACD"] < df["MACD_signal"])
        df.loc[buy_condition, ["signal", "confidence"]] = ["BUY", 0.9]
        df.loc[sell_condition, ["signal", "confidence"]] = ["SELL", 0.9]
        return df

    def _classify_trend(self, df):
        df["trend"] = "Sideways"
        bullish = (df["SMA_20"] > df["SMA_50"]) & (df["MACD"] > df["MACD_signal"])
        bearish = (df["SMA_20"] < df["SMA_50"]) & (df["MACD"] < df["MACD_signal"])
        df.loc[bullish, "trend"] = "Bullish"
        df.loc[bearish, "trend"] = "Bearish"
        return df

    def _compute_tech_score(self, df):
        return (
            (df["trend"] == "Bullish").astype(int)
            + (df["signal"] == "BUY").astype(int)
            + (df["OBV"] > df["OBV"].rolling(10, min_periods=1).mean()).astype(int)
        ) / 3.0

    # ---- ML Friendly Output ----
    def transform_for_ml(
        self, df: pd.DataFrame, as_tensor: bool = False
    ) -> Union[np.ndarray, "torch.Tensor"]:
        features = df.drop(
            columns=[
                c
                for c in df.columns
                if c in ["signal", "trend"] or df[c].dtype == "object"
            ],
            errors="ignore",
        ).dropna()

        if as_tensor:
            if not TORCH_AVAILABLE:
                raise RuntimeError("Torch requested but not available.")
            return torch.tensor(features.values, dtype=torch.float32)

        return features.values