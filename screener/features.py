import pandas as pd


class FeatureExtractor:
    """
    Extracts lightweight screening features from a DataFrame with
    columns: timestamp, open, high, low, close, volume, symbol.
    """

    @staticmethod
    def avg_daily_volume(df: pd.DataFrame, window: int = 20) -> pd.Series:
        # group by symbol then compute rolling mean of volume (resampled daily per symbol expected)
        return df.groupby("symbol")["volume"].transform(
            lambda s: s.rolling(window, min_periods=1).mean()
        )

    @staticmethod
    def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def momentum(df: pd.DataFrame, window: int = 10) -> pd.Series:
        return df.groupby("symbol")["close"].transform(
            lambda s: s.pct_change(periods=window).fillna(0)
        )

    @staticmethod
    def volatility(df: pd.DataFrame, window: int = 10) -> pd.Series:
        return df.groupby("symbol")["close"].transform(
            lambda s: s.pct_change().rolling(window, min_periods=1).std().fillna(0)
        )

    @staticmethod
    def compute_all(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["ADV20"] = FeatureExtractor.avg_daily_volume(out, window=20)
        out["ATR14"] = FeatureExtractor.atr(out, window=14)
        out["MOM10"] = FeatureExtractor.momentum(out, window=10)
        out["VOL10"] = FeatureExtractor.volatility(out, window=10)
        # basic rule scores
        out["rule_liquidity_ok"] = (out["ADV20"] >= out["volume"].median()).astype(int)
        out["rule_low_volatility"] = (out["VOL10"] <= out["VOL10"].median()).astype(int)
        out["rule_momentum_pos"] = (out["MOM10"] > 0).astype(int)
        return out
