# signal_engine/db_client.py
import pandas as pd
import numpy as np
from typing import List


def connect(*args, **kwargs):
    """
    Simple connect() stub required by tests.
    """
    return "connected"


class DBClient:
    """
    Minimal DBClient stub used by SignalEngine and tests.
    Provides fetch_ohlcv(symbols, lookback) returning a DataFrame.
    """

    def __init__(self, dsn: str = None):
        self.dsn = dsn

    def fetch_ohlcv(self, symbols: List[str], lookback: int = 100) -> pd.DataFrame:
        data = []
        for sym in symbols:
            for i in range(lookback):
                ts = pd.Timestamp.utcnow() - pd.Timedelta(minutes=(lookback - i))
                data.append(
                    {
                        "timestamp": ts,
                        "symbol": sym,
                        "open": 100 + np.random.randn(),
                        "high": 101 + abs(np.random.randn()),
                        "low": 99 - abs(np.random.randn()),
                        "close": 100 + np.random.randn(),
                        "volume": 100000 + int(abs(np.random.randn()) * 1000),
                    }
                )
        return pd.DataFrame(data)
