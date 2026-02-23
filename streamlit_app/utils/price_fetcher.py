# 📁 streamlit_app/utils/price_fetcher.py — Upgraded with mode-aware support

import pandas as pd
import requests
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PriceFetcher:
    def __init__(self, mode="paper"):
        self.mode = mode.lower()

    def fetch_price(self, symbol):
        if self.mode == "paper":
            return self._fetch_from_csv(symbol)
        elif self.mode == "dhan":
            return self._fetch_from_dhan(symbol)
        elif self.mode == "backtest":
            return self._fetch_historical(symbol)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def _fetch_from_csv(self, symbol):
        path = "logs/market/price_data.csv"
        if not os.path.exists(path):
            raise FileNotFoundError("CSV price log not found")
        df = pd.read_csv(path)
        latest = df[df["symbol"] == symbol].sort_values("timestamp").iloc[-1]
        return latest["close"]

    def _fetch_from_dhan(self, symbol):
        url = f"https://api.dhan.co/market/feed/{symbol}"
        headers = {
            "accept": "application/json",
            "access-token": os.getenv("DHAN_ACCESS_TOKEN"),
            "client-id": os.getenv("DHAN_CLIENT_ID"),
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return float(data["last_traded_price"])

    def _fetch_historical(self, symbol):
        df = pd.read_csv(f"data/backtest/{symbol}.csv")
        latest = df.sort_values("timestamp").iloc[-1]
        return latest["close"]

    def fetch_price_series(
        symbol: str, mode: str = "paper", **kwargs
    ) -> List[Dict[str, Any]]:
        """
        mode: 'paper' | 'backtest' | 'dhan'
        For 'dhan' mode, requires DHAN_API_KEY in env.
        Returns list of OHLCV dicts (open, high, low, close, volume, ts).
        """
        mode = (mode or "paper").lower()
        if mode == "paper":
            # return tiny demo ticks for UI/demo
            return [
                {
                    "open": 100.0,
                    "high": 100.5,
                    "low": 99.5,
                    "close": 100.0,
                    "volume": 10,
                    "ts": None,
                }
            ]
        if mode == "backtest":
            # expect kwargs["csv_path"] provided — load there (delegated to caller)
            csv = kwargs.get("csv_path")
            if not csv:
                raise RuntimeError("backtest mode requires csv_path kwarg")
            import pandas as pd

            df = pd.read_csv(csv)
            # map columns to ohlcv format — assume standard names
            rows = []
            for _, r in df.iterrows():
                rows.append(
                    {
                        "open": r["open"],
                        "high": r["high"],
                        "low": r["low"],
                        "close": r["close"],
                        "volume": r.get("volume", 0),
                        "ts": r.get("ts"),
                    }
                )
            return rows
        if mode in ("dhan", "live"):
            key = os.environ.get("DHAN_API_KEY") or os.environ.get("DHAN_KEY")
            if not key:
                raise RuntimeError(
                    "Dhan API key required for live mode (set DHAN_API_KEY)."
                )
            # minimal HTTP wrapper (the real implementation can be more sophisticated)
            # Here we only raise descriptive errors if call fails.
            import requests

            base = os.environ.get("DHAN_BASE_URL", "https://api.dhan.com")
            try:
                r = requests.get(
                    f"{base}/quotes/{symbol}",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=5,
                )
                r.raise_for_status()
                data = r.json()
                # adapt to expected ohlcv list
                return data.get("ohlcv", [])
            except Exception as e:
                logger.exception("Dhan fetch failed: %s", e)
                raise
        raise ValueError("Unknown mode: %s" % mode)
