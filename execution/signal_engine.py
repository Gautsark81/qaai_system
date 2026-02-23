# qaai_system/execution/signal_engine.py
from __future__ import annotations

"""
SignalEngine - deterministic signal engine for unit tests.

Exposes:
- run(symbols) -> pd.DataFrame
- generate_signals(...)
- helper methods: _dynamic_sl_tp, _size_by_drawdown, _blend_scores_and_explain
- register_trade_result(...)
"""

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger("SignalEngine")
logger.setLevel(logging.INFO)

# Optional ML scoring hook
try:
    from screening.watchlist_ml import score_candidates  # type: ignore
except Exception:
    score_candidates = None


class SignalEngine:
    def __init__(self):
        self.trades: List[Dict[str, Any]] = []
        self.trade_results: List[Dict[str, Any]] = []

        self.buy_threshold = 0.7
        self.sell_threshold = -0.7
        self.mode = "test"

        self.risk_config = {
            "base_sl_mult": 1.0,
            "base_tp_mult": 2.0,
            "regime_multiplier": {
                "bull": {"sl": 1.0, "tp": 1.2},
                "bear": {"sl": 1.2, "tp": 0.9},
                "sideways": {"sl": 1.0, "tp": 1.0},
            },
            "drawdown_sizing": {"threshold": 0.05, "size_mult": 0.5},
            "blended_score_weights": {"rule": 0.5, "ml": 0.5},
            "min_position_size": 1,
            "max_position_size": 100,
            "volatility_scale": True,
        }

        self._feedback_lock = threading.Lock()
        self._feedback_store: List[Dict[str, Any]] = []
        self._feedback_log = "signal_feedback_log.csv"
        self._feedback_batch = 10
        self.history_window = 60

    # ---------------------------------------------------------------
    # Test-facing API
    # ---------------------------------------------------------------
    def run(self, symbols: List[str]) -> pd.DataFrame:
        return self.generate_signals(symbols)

    def generate_signals(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        now = datetime.utcnow()
        rows: List[Dict[str, Any]] = []

        for sym in symbols or ["MOCK"]:
            price = 100.0
            atr = 1.0
            side = "BUY"
            sl = price - atr * self.risk_config["base_sl_mult"]
            tp = price + atr * self.risk_config["base_tp_mult"]

            rows.append(
                {
                    "timestamp": now,
                    "symbol": sym,
                    "price": float(price),
                    "atr": float(atr),
                    "signal_strength": 0.8,
                    "side": side,
                    "sl_scaled": float(sl),
                    "tp_scaled": float(tp),
                    "position_size": int(self.risk_config["min_position_size"]),
                    "strategy_id": "rule_v1",
                }
            )

        return pd.DataFrame(rows)

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------
    def _volatility_relative_scale(self, df: pd.DataFrame) -> pd.Series:
        if "atr" not in df.columns:
            return pd.Series(1.0, index=df.index)
        median_atr = df["atr"].median() or 1.0
        return (df["atr"] / median_atr).fillna(1.0).replace([pd.NA, None], 1.0)

    def _dynamic_sl_tp(self, df: pd.DataFrame, regime: str) -> pd.DataFrame:
        cfg = self.risk_config
        base_sl, base_tp = cfg["base_sl_mult"], cfg["base_tp_mult"]
        regime_entry = cfg["regime_multiplier"].get(regime, {"sl": 1.0, "tp": 1.0})

        vol_scale = (
            self._volatility_relative_scale(df) if cfg.get("volatility_scale") else 1.0
        )
        price = df.get("price", pd.Series(0.0, index=df.index))
        atr = df.get("atr", pd.Series(1.0, index=df.index))

        out = df.copy()
        out["sl_scaled"] = price - atr * base_sl * regime_entry["sl"] * vol_scale
        out["tp_scaled"] = price + atr * base_tp * regime_entry["tp"] * vol_scale

        # Flip for SELL
        if "side" in out.columns:
            mask = out["side"].astype(str).str.upper() == "SELL"
            out.loc[mask, "sl_scaled"] = (
                price + atr * base_sl * regime_entry["sl"] * vol_scale
            )
            out.loc[mask, "tp_scaled"] = (
                price - atr * base_tp * regime_entry["tp"] * vol_scale
            )

        return out

    def _size_by_drawdown(
        self, df: pd.DataFrame, current_drawdown: Optional[float] = None
    ) -> pd.DataFrame:
        cfg = self.risk_config
        min_size, max_size = cfg["min_position_size"], cfg["max_position_size"]

        atr = df.get("atr", pd.Series(1.0, index=df.index)).replace(0, 1.0).fillna(1.0)
        inv_atr = (1.0 / atr).fillna(1.0).replace([pd.NA, None], 1.0)
        base = inv_atr / (inv_atr.max() or 1.0)

        raw_size = (base * (max_size - min_size) + min_size).round().astype(int)

        out = df.copy()
        out["position_size"] = raw_size.clip(lower=min_size)

        dd_cfg = cfg["drawdown_sizing"]
        if current_drawdown is not None and current_drawdown >= dd_cfg["threshold"]:
            out["position_size"] = (
                (out["position_size"] * dd_cfg["size_mult"])
                .clip(lower=min_size)
                .astype(int)
            )

        return out

    def _blend_scores_and_explain(self, df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.risk_config
        w_rule, w_ml = (
            cfg["blended_score_weights"]["rule"],
            cfg["blended_score_weights"]["ml"],
        )

        rule_s = df.get("signal_strength", pd.Series(0.5, index=df.index)).fillna(0.5)
        ml_s = df.get("ml_score", pd.Series(0.5, index=df.index)).fillna(0.5)

        blended = (w_rule * rule_s + w_ml * ml_s) / (w_rule + w_ml)
        out = df.copy()
        out["blended_score"] = blended.clip(0.0, 1.0)

        def _reason(row):
            return (
                f"rule={row.get('signal_strength',0.0):.3f} | "
                f"ml={row.get('ml_score',0.5):.3f} | "
                f"blended={row.get('blended_score',0.0):.3f} | "
                f"side={row.get('side','N/A')} | "
                f"price={row.get('price',0.0)}"
            )

        out["reason"] = out.apply(_reason, axis=1)
        return out

    # ---------------------------------------------------------------
    # Feedback
    # ---------------------------------------------------------------
    def register_trade_result(
        self,
        trade_id: str,
        pnl: float,
        sl_hit: bool,
        tp_hit: bool,
        meta: Optional[Dict[str, Any]] = None,
    ):
        """
        Record the result of a completed trade for feedback loops.
        """
        entry = {
            "trade_id": trade_id,
            "pnl": pnl,
            "sl_hit": sl_hit,
            "tp_hit": tp_hit,
            "meta": meta or {},
        }
        self.trade_results.append(entry)

        with self._feedback_lock:
            self._feedback_store.append(entry)
            try:
                pd.DataFrame(self._feedback_store).to_csv(
                    self._feedback_log, index=False
                )
            except Exception:
                pass

            # Auto-tune based on recent losses
            if len(self._feedback_store) >= self._feedback_batch:
                recent = pd.DataFrame(self._feedback_store[-self._feedback_batch :])
                if not recent.empty and "pnl" in recent.columns:
                    loss_rate = (recent["pnl"] < 0).mean()
                    if loss_rate > 0.6:
                        self.risk_config["base_sl_mult"] *= 0.95
                        self.risk_config["base_tp_mult"] *= 1.05
                        logger.info("Auto-tune applied, loss_rate=%.2f", loss_rate)


def persist_model(*args, **kwargs):
    logger.debug("persist_model noop")
