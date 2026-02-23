# modules/backtest/noise_models.py

import numpy as np
import pandas as pd


class NoiseModels:
    @staticmethod
    def add_slippage(price: float | pd.Series, slippage_bps: int = 5):
        """
        Inject slippage +/- slippage_bps basis points (bps) around price.
        1 bp = 0.01%. Default 5 bps = 0.05%
        Deterministic for scalar; vectorized for Series.
        """
        if isinstance(price, pd.Series):
            rnd = (
                np.random.uniform(-slippage_bps, slippage_bps, size=len(price)) / 10_000
            )
            return price * (1 + rnd)

        rnd = np.random.uniform(-slippage_bps, slippage_bps) / 10_000
        return price * (1 + rnd)

    @staticmethod
    def add_spread(mid_price: float | pd.Series, spread_bps: int = 10):
        """
        Convert a mid price to (bid, ask) using total spread in bps.
        Returns tuple (bid, ask); vectorized for Series.
        """
        half = (spread_bps / 10_000) / 2

        if isinstance(mid_price, pd.Series):
            bid = mid_price * (1 - half)
            ask = mid_price * (1 + half)
            return bid, ask

        return mid_price * (1 - half), mid_price * (1 + half)

    @staticmethod
    def latency_ms(mean_ms: int = 80, jitter_ms: int = 40):
        """
        Sample a non-negative latency in ms with simple uniform jitter.
        """
        lat = np.random.uniform(mean_ms - jitter_ms, mean_ms + jitter_ms)
        return max(0.0, float(lat))
