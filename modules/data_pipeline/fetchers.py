from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
import numpy as np

class AbstractFetcher(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, start: str, end: str, timeframe: str = "1d") -> pd.DataFrame:
        """Return DataFrame indexed by timestamp with columns open,high,low,close,volume"""

    @abstractmethod
    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Return fundamentals as a dict"""

class DummyFetcher(AbstractFetcher):
    def fetch_ohlcv(self, symbol: str, start: str, end: str, timeframe: str = "1d") -> pd.DataFrame:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        idx = pd.date_range(start=start_dt, end=end_dt, freq="D")
        n = len(idx)
        seed = abs(hash(symbol)) % 9973
        rng = np.random.RandomState(seed)
        base = 100.0 + (seed % 50)
        t = np.arange(n)
        price = base + 2.0 * np.sin(t / 3.0) + rng.normal(0, 0.5, size=n)
        high = price + rng.uniform(0.1, 1.0, size=n)
        low = price - rng.uniform(0.1, 1.0, size=n)
        open_ = price + rng.normal(0, 0.2, size=n)
        close = price + rng.normal(0, 0.2, size=n)
        volume = rng.randint(1000, 10000, size=n).astype(float)
        df = pd.DataFrame({
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }, index=idx)
        df.index.name = "timestamp"
        return df

    def fetch_fundamentals(self, symbol: str):
        seed = abs(hash(symbol)) % 9973
        return {
            "symbol": symbol,
            "market_cap": float(1e9 + (seed % 100) * 1e6),
            "pe": float(10 + (seed % 20)),
            "pb": float(1 + (seed % 5)),
            "sector": "DummySector",
        }
