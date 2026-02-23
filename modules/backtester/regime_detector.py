import pandas as pd


class RegimeDetector:
    """
    Simple MA-based regime classifier for bull/bear/sideways.
    Uses rolling means; requires at least `lookback` data points.
    """

    @staticmethod
    def detect_regime(prices: pd.Series, lookback: int = 50) -> str:
        if len(prices) < max(lookback, 3):
            return "UNKNOWN"
        short = prices.rolling(max(2, lookback // 2), min_periods=1).mean()
        long = prices.rolling(lookback, min_periods=1).mean()
        diff = short.iloc[-1] - long.iloc[-1]
        thr = prices.std() * 0.01  # tiny threshold against ties
        if diff > thr:
            return "BULL"
        if diff < -thr:
            return "BEAR"
        return "SIDEWAYS"
