import pandas as pd
from qaai_system.signal_engine.signal_engine_supercharged import (
    SignalEngineSupercharged,
)


class FeatureExtractor:
    """
    Computes reusable technical features for screening and meta-screening.
    """

    @staticmethod
    def compute_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute a standardized feature set for each symbol.
        """
        se = SignalEngineSupercharged()
        out = df.copy()

        # Basic indicators
        out["RSI14"] = se.rsi(out["close"], window=14)
        out["ATR14"] = se.atr(out, window=14)
        # Momentum computed manually since se.momentum() is missing
        out["MOM10"] = out["close"].diff(10)

        # Average Daily Volume over 20 periods (ADV20)
        out["ADV20"] = out["volume"].rolling(20).mean()

        # Moving averages
        out["SMA20"] = out["close"].rolling(20).mean()
        out["SMA50"] = out["close"].rolling(50).mean()

        # Volatility features
        out["RET"] = out["close"].pct_change()
        out["VOL10"] = out["RET"].rolling(10).std()

        # Optional: fill NaN for initial rows
        out.fillna(0, inplace=True)

        return out
