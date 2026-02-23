# qaai_system/backtester/backtester.py
"""
Backtester — Phase 2 Upgrade (Portfolio + Risk Metrics)

Features:
 - Strategy registry (register_strategy / list_strategies)
 - run() for single symbol
 - run_portfolio() for multiple symbols with aggregated PnL
 - simulate_execution: slippage + latency + FIFO
 - returns PnL DataFrame + summary dict
 - persists trade log JSONL
 - feedback hooks for ML/learning components
 - risk metrics: Sharpe ratio, max drawdown, volatility
"""
from __future__ import annotations
from typing import Callable, Dict, Any, List, Optional, Union
import time
import uuid
import json
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime
from qaai_system.db.db_utils import DBManager
from infra.pnl_calculator import PnLCalculator

TRADE_LOG_DIR = "logs/trades"
os.makedirs(TRADE_LOG_DIR, exist_ok=True)


class Backtester:
    def __init__(
        self, db_url: str = "sqlite:///qaai.db", account_equity: float = 1_000_000.0
    ):
        self.db = DBManager(db_url)
        self.pnl_calc = PnLCalculator(account_equity)
        self.strategy_registry: Dict[
            str, Callable[[pd.DataFrame], List[Dict[str, Any]]]
        ] = {}
        self.default_slippage_pct = 0.001
        self.default_latency_ms = 50
        self.on_feedback_hooks: List[Callable[[Dict[str, Any]], None]] = []

    # ---------------- Strategy registry ----------------
    def register_strategy(
        self, name: str, fn: Callable[[pd.DataFrame], List[Dict[str, Any]]]
    ) -> None:
        self.strategy_registry[name] = fn

    def unregister_strategy(self, name: str) -> None:
        if name in self.strategy_registry:
            del self.strategy_registry[name]

    def list_strategies(self) -> List[str]:
        return list(self.strategy_registry.keys())

    # ---------------- Execution simulation ----------------
    def _apply_slippage(
        self, price: float, side: str, slippage_pct: Optional[float] = None
    ) -> float:
        if price is None:
            return price
        sl_pct = slippage_pct if slippage_pct is not None else self.default_slippage_pct
        rnd = 0.5 + random.random()
        slip = price * sl_pct * rnd
        side_up = str(side).upper() in ("BUY", "LONG")
        return float(price + slip if side_up else price - slip)

    def _simulate_latency(self, ms: int) -> None:
        if ms and ms > 0:
            time.sleep(ms / 1000.0)

    def simulate_execution(
        self,
        planned_trades: List[Dict[str, Any]],
        slippage_pct: Optional[float] = None,
        latency_ms: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        fills: List[Dict[str, Any]] = []

        def sort_key(t: Dict[str, Any]):
            ts = t.get("timestamp")
            try:
                return pd.to_datetime(ts) if ts is not None else pd.Timestamp.utcnow()
            except Exception:
                return pd.Timestamp.utcnow()

        planned_trades_sorted = sorted(planned_trades, key=sort_key)

        for t in planned_trades_sorted:
            raw_price = t.get("entry_price") or t.get("price") or t.get("entry") or None
            try:
                price = float(raw_price) if raw_price is not None else None
            except Exception:
                price = None

            side = t.get("side", "BUY")
            qty = int(t.get("quantity") or t.get("qty") or 1)

            self._simulate_latency(
                latency_ms if latency_ms is not None else self.default_latency_ms
            )

            exec_price = (
                self._apply_slippage(price, side, slippage_pct=slippage_pct)
                if price is not None
                else None
            )

            fill: Dict[str, Any] = {
                "fill_id": str(uuid.uuid4()),
                "order_id": t.get("order_id") or str(uuid.uuid4()),
                "symbol": t.get("symbol"),
                "side": side,
                "qty": qty,
                "price": float(exec_price) if exec_price is not None else None,
                "strategy_id": t.get("strategy_id") or t.get("strategy") or None,
                "timestamp": pd.Timestamp.utcnow().isoformat(),
            }

            canonical_keys = {
                "fill_id",
                "order_id",
                "price",
                "qty",
                "symbol",
                "side",
                "strategy_id",
                "timestamp",
            }
            for k, v in t.items():
                if k not in canonical_keys:
                    fill[k] = v

            try:
                fill["meta"] = {k: v for k, v in t.items()}
            except Exception:
                fill["meta"] = str(t)

            fills.append(fill)

        return fills

    # ---------------- Trade log persistence ----------------
    def _persist_trade_log(
        self, trades: List[Dict[str, Any]], log_dir: str = TRADE_LOG_DIR
    ) -> str:
        os.makedirs(log_dir, exist_ok=True)
        fname = os.path.join(
            log_dir, f"backtest_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

        def json_converter(o):
            if hasattr(o, "isoformat"):
                return o.isoformat()
            return str(o)

        with open(fname, "w", encoding="utf-8") as fh:
            for trade in trades:
                fh.write(json.dumps(trade, default=json_converter) + "\n")

        return fname

    # ---------------- Feedback hooks ----------------
    def register_feedback_hook(self, hook: Callable[[Dict[str, Any]], None]) -> None:
        self.on_feedback_hooks.append(hook)

    def _call_feedback_hooks(self, trade_record: Dict[str, Any]) -> None:
        for h in self.on_feedback_hooks:
            try:
                h(trade_record)
            except Exception:
                pass

    # ---------------- Risk metrics ----------------
    def _compute_risk_metrics(self, pnl_df: pd.DataFrame) -> Dict[str, float]:
        if pnl_df is None or pnl_df.empty or "total_pnl" not in pnl_df.columns:
            return {}

        pnl_series = pnl_df["total_pnl"].fillna(0.0).values
        cum_pnl = pnl_series.cumsum()

        # Daily returns approximation
        returns = np.diff(cum_pnl, prepend=0)

        # Sharpe ratio (annualized, risk-free = 0)
        sharpe = (
            (returns.mean() / (returns.std() + 1e-8)) * np.sqrt(252)
            if returns.std() > 0
            else 0.0
        )

        # Max drawdown
        running_max = np.maximum.accumulate(cum_pnl)
        drawdowns = running_max - cum_pnl
        max_dd = float(drawdowns.max())

        return {
            "sharpe_ratio": float(sharpe),
            "max_drawdown": max_dd,
            "volatility": float(returns.std()),
        }

    # ---------------- Single-symbol backtest ----------------
    def run(
        self,
        symbol: str,
        start_date,
        end_date,
        strategy: Union[str, Callable[[pd.DataFrame], List[Dict[str, Any]]]],
        *,
        slippage_pct: Optional[float] = None,
        latency_ms: Optional[int] = None,
        persist_trades: bool = True,
    ) -> Dict[str, Any]:
        df = self.db.get_ohlcv_df(symbol, start_date, end_date)
        if df is None or df.empty:
            raise ValueError(
                f"No OHLCV data for {symbol} in range {start_date}..{end_date}"
            )

        if isinstance(strategy, str):
            if strategy not in self.strategy_registry:
                raise ValueError(f"strategy '{strategy}' not registered")
            strategy_fn = self.strategy_registry[strategy]
        else:
            strategy_fn = strategy

        planned_trades = strategy_fn(df.copy()) or []
        if not isinstance(planned_trades, list):
            raise ValueError("strategy must return a list of trade dicts")

        normalized: List[Dict[str, Any]] = []
        for t in planned_trades:
            if not isinstance(t, dict):
                continue
            norm = {
                "symbol": t.get("symbol", symbol),
                "side": t.get("side", "BUY"),
                "quantity": int(t.get("quantity") or t.get("qty") or 1),
                "entry_price": t.get("entry_price") or t.get("price") or None,
                "strategy_id": t.get("strategy_id")
                or getattr(strategy_fn, "__name__", "strategy"),
            }
            for k, v in t.items():
                if k not in norm:
                    norm[k] = v
            normalized.append(norm)

        fills = self.simulate_execution(
            normalized, slippage_pct=slippage_pct, latency_ms=latency_ms
        )

        trades_for_pnl: List[Dict[str, Any]] = []
        for f in fills:
            entry_price = (
                f.get("entry_price")
                if f.get("entry_price") is not None
                else f.get("price")
            )
            exit_price = f.get("exit_price")
            status = f.get("status") or ("closed" if exit_price is not None else "open")
            trades_for_pnl.append(
                {
                    "symbol": f.get("symbol"),
                    "side": f.get("side"),
                    "quantity": int(f.get("qty") or f.get("quantity") or 1),
                    "entry_price": (
                        float(entry_price) if entry_price is not None else None
                    ),
                    "exit_price": float(exit_price) if exit_price is not None else None,
                    "status": status,
                    "strategy_id": f.get("strategy_id"),
                    "timestamp": f.get("timestamp"),
                    "fill_id": f.get("fill_id"),
                    "reason": f.get("reason"),
                }
            )

        pnl_df = self.pnl_calc.compute_portfolio_pnl(trades_for_pnl, to_dataframe=True)
        summary = self.pnl_calc.summarize_portfolio(trades_for_pnl)

        # Add risk metrics
        risk = self._compute_risk_metrics(pnl_df)
        summary.update(risk)

        trade_log_path: Optional[str] = None
        if persist_trades:
            trade_log_path = self._persist_trade_log(fills)

        for t in trades_for_pnl:
            entry = t.get("entry_price")
            exit_p = t.get("exit_price")
            qty = t.get("quantity", 1)
            side = str(t.get("side", "BUY")).upper()
            pnl_value = 0.0
            if entry is not None and exit_p is not None:
                pnl_value = (
                    (exit_p - entry) * qty
                    if side in ("BUY", "LONG")
                    else (entry - exit_p) * qty
                )
            feedback = {"trade": t, "pnl": pnl_value, "summary": summary}
            self._call_feedback_hooks(feedback)

        return {
            "pnl_df": pnl_df,
            "summary": summary,
            "fills": fills,
            "trade_log_path": trade_log_path,
        }

    # ---------------- Portfolio backtest ----------------
    def run_portfolio(
        self,
        symbols: List[str],
        start_date,
        end_date,
        strategy: Union[str, Callable[[pd.DataFrame], List[Dict[str, Any]]]],
        *,
        slippage_pct: Optional[float] = None,
        latency_ms: Optional[int] = None,
        persist_trades: bool = True,
        capital_per_symbol: Optional[float] = None,
    ) -> Dict[str, Any]:
        all_trades, all_fills = [], []

        for sym in symbols:
            result = self.run(
                sym,
                start_date,
                end_date,
                strategy,
                slippage_pct=slippage_pct,
                latency_ms=latency_ms,
                persist_trades=False,
            )
            trades = result["pnl_df"].to_dict("records")
            fills = result["fills"]

            if capital_per_symbol:
                for t in trades:
                    if t.get("entry_price"):
                        max_qty = int(capital_per_symbol / t["entry_price"])
                        t["quantity"] = max_qty

            all_trades.extend(trades)
            all_fills.extend(fills)

        pnl_df = self.pnl_calc.compute_portfolio_pnl(all_trades, to_dataframe=True)
        summary = self.pnl_calc.summarize_portfolio(all_trades)

        # Add risk metrics
        risk = self._compute_risk_metrics(pnl_df)
        summary.update(risk)

        trade_log_path = self._persist_trade_log(all_fills) if persist_trades else None

        return {
            "pnl_df": pnl_df,
            "summary": summary,
            "fills": all_fills,
            "trade_log_path": trade_log_path,
        }
