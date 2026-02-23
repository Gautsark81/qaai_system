from __future__ import annotations

"""
Evaluate trade/signal quality & auto-tune thresholds.

This module provides:
- evaluate_signal_quality(trade_log) -> pd.DataFrame with columns:
    ['symbol', 'total_trades', 'win_rate', 'avg_pnl', 'quality_score']
  Accepts trade_log as a DataFrame, list of dicts, or dict-of-lists / dict-of-scalars.

- auto_tune_thresholds(trade_log, current_buy=0.5, current_sell=0.5)
  Flexible: tests call with just (trade_log,), so we support that as well.
"""

from typing import Any, Dict, List
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _normalize_to_df(trade_log: Any) -> pd.DataFrame:
    if trade_log is None:
        return pd.DataFrame()
    if isinstance(trade_log, pd.DataFrame):
        return trade_log.copy()
    if isinstance(trade_log, dict):
        if all(
            not isinstance(v, (list, tuple, pd.Series, np.ndarray))
            for v in trade_log.values()
        ):
            return pd.DataFrame([trade_log])
        try:
            return pd.DataFrame(trade_log)
        except Exception:
            return pd.DataFrame([trade_log])
    if isinstance(trade_log, list):
        try:
            return pd.DataFrame(trade_log)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def evaluate_signal_quality(trade_log: Any) -> pd.DataFrame:
    df = _normalize_to_df(trade_log)
    if df.empty:
        return pd.DataFrame(
            columns=["symbol", "total_trades", "win_rate", "avg_pnl", "quality_score"]
        )
    if "symbol" not in df.columns or "pnl" not in df.columns:
        raise ValueError("trade_log must contain 'symbol' and 'pnl' columns")

    df["symbol"] = df["symbol"].astype(str)
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0.0)

    rows: List[Dict[str, Any]] = []
    for sym, g in df.groupby("symbol", dropna=False):
        total = len(g)
        wins = (g["pnl"] > 0).sum()
        win_rate = wins / total if total else 0.0
        avg_pnl = g["pnl"].mean() if total else 0.0
        pnl_score = (np.tanh(avg_pnl / (abs(avg_pnl) + 1.0)) + 1.0) / 2.0
        quality_score = float(np.clip(0.6 * win_rate + 0.4 * pnl_score, 0, 1))
        rows.append(
            {
                "symbol": sym,
                "total_trades": int(total),
                "win_rate": float(win_rate),
                "avg_pnl": float(avg_pnl),
                "quality_score": quality_score,
            }
        )
    return pd.DataFrame(rows).sort_values("symbol").reset_index(drop=True)


def auto_tune_thresholds(
    trade_log: Any, current_buy: float = 0.5, current_sell: float = 0.5
) -> Dict[str, float]:
    dfq = evaluate_signal_quality(trade_log)
    if dfq.empty:
        return {
            "confidence_threshold": current_buy,
            "sl_multiplier": current_sell,
            "tp_multiplier": 1.0,
        }
    mean_q = dfq["quality_score"].mean()
    confidence_threshold = float(np.clip(current_buy + 0.1 * (mean_q - 0.5), 0.3, 0.7))
    sl_multiplier = float(np.clip(current_sell + 0.5 * (0.5 - mean_q), 0.1, 5.0))
    tp_multiplier = float(np.clip(1.0 + mean_q, 0.5, 3.0))
    return {
        "confidence_threshold": confidence_threshold,
        "sl_multiplier": sl_multiplier,
        "tp_multiplier": tp_multiplier,
    }
