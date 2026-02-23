# File: qaai_system/signal_engine/signal_engine_supercharged.py

import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# Lazy Torch Import (Prevents Windows shm.dll crash during pytest collect)
# ----------------------------------------------------------------------

try:
    import torch  # type: ignore
    TORCH_AVAILABLE = True
except Exception:  # noqa: BLE001
    torch = None  # type: ignore
    TORCH_AVAILABLE = False


class SignalEngineSupercharged:
    """Advanced technical indicator engine with ML-ready outputs."""

    # ---------------------------
    # Core Indicators
    # ---------------------------
    @staticmethod
    def sma(series, window=14):
        return series.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def ema(series, window=14):
        return series.ewm(span=window, adjust=False).mean()

    @staticmethod
    def rsi(series, window=14):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-8)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def obv(df):
        direction = np.sign(df["close"].diff().fillna(0))
        obv = (direction * df["volume"]).cumsum()
        return obv

    @staticmethod
    def atr(df, window=14):
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def bollinger_bands(series, window=20, n_std=2):
        sma = series.rolling(window=window, min_periods=1).mean()
        std = series.rolling(window=window, min_periods=1).std(ddof=0)
        upper = sma + n_std * std
        lower = sma - n_std * std
        width = upper - lower
        return upper, lower, width

    @staticmethod
    def supertrend(df, period=7, multiplier=1):
        hl2 = (df["high"] + df["low"]) / 2
        atr = SignalEngineSupercharged.atr(df, window=period)
        upperband = hl2 + (multiplier * atr)
        lowerband = hl2 - (multiplier * atr)

        st = pd.Series(index=df.index, dtype=float)
        in_uptrend = True

        for i in range(len(df)):
            if i < period:
                st.iloc[i] = np.nan
                continue
            if df["close"].iloc[i] > upperband.iloc[i - 1]:
                in_uptrend = True
            elif df["close"].iloc[i] < lowerband.iloc[i - 1]:
                in_uptrend = False
            st.iloc[i] = 1 if in_uptrend else -1
        return st

    # ---------------------------
    # ML / Feature Engine
    # ---------------------------
    def compute_all_indicators(self, df):
        df = df.copy()
        df["SMA20"] = self.sma(df["close"], window=20)
        df["EMA20"] = self.ema(df["close"], window=20)
        df["RSI14"] = self.rsi(df["close"], window=14)
        macd, signal = self.macd(df["close"])
        df["MACD"] = macd
        df["MACD_SIGNAL"] = signal
        df["ATR14"] = self.atr(df, window=14)
        bb_up, bb_low, bb_width = self.bollinger_bands(df["close"], window=20)
        df["BB_UP"] = bb_up
        df["BB_LOW"] = bb_low
        df["BB_WIDTH"] = bb_width
        df["OBV"] = self.obv(df)
        return df

    def transform_for_ml(self, df, as_tensor=False):
        df = self.compute_all_indicators(df)

        features = [
            "SMA20",
            "EMA20",
            "RSI14",
            "MACD",
            "MACD_SIGNAL",
            "ATR14",
            "BB_UP",
            "BB_LOW",
            "BB_WIDTH",
            "OBV",
        ]

        X = df[features].fillna(0).values

        if as_tensor:
            if not TORCH_AVAILABLE:
                raise RuntimeError("Torch requested but not available.")
            return torch.tensor(X, dtype=torch.float32)

        return pd.DataFrame(X, columns=features)

    # ---------------------------
    # Unified Signal Generation
    # ---------------------------
    def generate_signals(self, df, symbol: str = "UNKNOWN"):
        df_ind = self.compute_all_indicators(df)

        signal = 0
        score = 0.0

        if not df_ind.empty:
            rsi_latest = df_ind["RSI14"].iloc[-1]
            if rsi_latest < 30:
                signal, score = 1, 1.0
            elif rsi_latest > 70:
                signal, score = -1, 1.0

        return [{"symbol": symbol, "signal": signal, "score": score}]