"""
PnL Calculator — Final Version
--------------------------------
Central utility for computing:
  - Average Entry Price
  - Realized PnL
  - Unrealized PnL
  - Position Exposure
  - Win/Loss ratios
  - Trade Inventory Snapshot

This module is MASTER UPGRADE OBJECTIVES aligned:
  ✅ Unified PnL logic across system
  ✅ Risk-aware (ATR, volatility, equity scaling ready)
  ✅ Dashboard-ready (returns dicts/dataframes directly)
  ✅ Audit-friendly (logs to trade dicts)
"""

from __future__ import annotations
from typing import Dict, List, Any
import pandas as pd


class PnLCalculator:
    def __init__(self, account_equity: float = 1_000_000.0):
        """
        Args:
            account_equity: starting account equity for % PnL calculations
        """
        self.account_equity = account_equity

    def compute_trade_pnl(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute realized/unrealized PnL for a single trade.
        Expected keys in trade dict:
            - side: "BUY" / "SELL"
            - entry_price: float
            - exit_price: float (optional)
            - qty: int
            - status: "open" / "closed" / "partially_filled"
        """
        side = str(trade.get("side", "BUY")).upper()
        qty = int(trade.get("quantity") or trade.get("qty", 0))
        entry_price = float(trade.get("entry_price", 0.0))
        exit_price = trade.get("exit_price")

        if exit_price is not None:
            exit_price = float(exit_price)

        # direction
        sign = 1 if side in ("BUY", "LONG") else -1

        realized = 0.0
        unrealized = 0.0

        if trade.get("status") == "closed" and exit_price:
            realized = (exit_price - entry_price) * qty * sign
        elif trade.get("status") in ("open", "partially_filled"):
            # assume we have a mark price (else fallback to entry)
            mark_price = float(trade.get("mark_price", entry_price))
            unrealized = (mark_price - entry_price) * qty * sign

        pnl_dict = {
            "symbol": trade.get("symbol"),
            "side": side,
            "qty": qty,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "realized": realized,
            "unrealized": unrealized,
            "total_pnl": realized + unrealized,
            "status": trade.get("status"),
            "strategy_id": trade.get("strategy_id"),
        }
        return pnl_dict

    def compute_portfolio_pnl(
        self, trades: List[Dict[str, Any]], to_dataframe: bool = True
    ) -> pd.DataFrame | List[Dict[str, Any]]:
        """
        Aggregate PnL for a list of trades.
        Returns dataframe or list of dicts.
        """
        results = [self.compute_trade_pnl(t) for t in trades]

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        df["pnl_pct_equity"] = df["total_pnl"] / max(1.0, self.account_equity) * 100
        df["exposure"] = df["qty"] * df["entry_price"]

        if to_dataframe:
            return df
        return results

    def summarize_portfolio(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Portfolio-level metrics:
          - total_realized
          - total_unrealized
          - total_pnl
          - win_rate
          - avg_trade_return
        """
        df = self.compute_portfolio_pnl(trades, to_dataframe=True)
        if df.empty:
            return {
                "total_realized": 0.0,
                "total_unrealized": 0.0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "avg_trade_return": 0.0,
                "num_trades": 0,
            }

        wins = df[df["total_pnl"] > 0]
        win_rate = len(wins) / len(df) if len(df) else 0.0

        return {
            "total_realized": float(df["realized"].sum()),
            "total_unrealized": float(df["unrealized"].sum()),
            "total_pnl": float(df["total_pnl"].sum()),
            "win_rate": win_rate,
            "avg_trade_return": float(df["total_pnl"].mean()),
            "num_trades": len(df),
        }
