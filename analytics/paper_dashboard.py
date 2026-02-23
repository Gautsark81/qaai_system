from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np


class PaperPerformanceDashboard:
    """
    Deterministic, append-only paper trading analytics.
    No live dependencies. Restart-safe.
    """

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

        self.trade_log = self.root / "trade_log.jsonl"
        self.equity_curve = self.root / "equity_curve.csv"
        self.daily_metrics = self.root / "daily_metrics.csv"

    # ---------- INGEST ----------

    def record_trade(self, trade: dict) -> None:
        trade["ts_utc"] = datetime.utcnow().isoformat()
        with self.trade_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trade) + "\n")

    # ---------- COMPUTE ----------

    def build_equity_curve(self, starting_capital: float = 100_000.0) -> pd.DataFrame:
        trades = self._load_trades()
        if trades.empty:
            return pd.DataFrame()

        trades["cum_pnl"] = trades["pnl"].cumsum()
        trades["equity"] = starting_capital + trades["cum_pnl"]

        df = trades[["timestamp", "equity"]].copy()
        df.to_csv(self.equity_curve, index=False)
        return df

    def build_daily_metrics(self) -> pd.DataFrame:
        eq = pd.read_csv(self.equity_curve, parse_dates=["timestamp"])
        eq["date"] = eq["timestamp"].dt.date

        daily = eq.groupby("date")["equity"].last().pct_change().dropna()
        metrics = pd.DataFrame({
            "date": daily.index,
            "daily_return": daily.values,
            "volatility": daily.rolling(20).std(),
            "sharpe": (daily.mean() / daily.std()) * np.sqrt(252)
        })

        metrics.to_csv(self.daily_metrics, index=False)
        return metrics

    # ---------- INTERNAL ----------

    def _load_trades(self) -> pd.DataFrame:
        if not self.trade_log.exists():
            return pd.DataFrame()

        rows = [json.loads(l) for l in self.trade_log.read_text().splitlines()]
        return pd.DataFrame(rows)
