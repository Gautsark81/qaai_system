"""
signal_engine/signal_generator.py — FINAL SUPERCHARGED with thread-safe feedback loop

Features:
- Dynamic SL/TP scaling based on ATR & detected regime
- Drawdown-aware position sizing
- Blended scoring (rule + ML) and human-friendly explain reason
- Thread-safe register_trade_result with CSV persistence and batch auto-tune
- Defensive: works without ML/models/DB (mock data / fallbacks)
"""

import sys
import importlib
import os
import threading
import logging
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any

_real = importlib.import_module("qaai_system.signal_engine.signal_generator")
sys.modules[__name__] = _real


try:
    from .signal_engine import SignalEngine
except Exception:
    SignalEngine = None

mod = importlib.import_module("qaai_system.signal_engine.signal_generator")
sys.modules[__name__] = mod

# ✅ Direct import from screening — no self-import confusion
from screening.signal_generator import generate_signals

# DB client — fallback to mock if missing
try:
    from signal_engine.db_client import DBClient
except ImportError:

    class DBClient:
        def __init__(self, dsn=None):
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
                            "high": 101 + np.random.rand(),
                            "low": 99 - np.random.rand(),
                            "close": 100 + np.random.randn(),
                            "volume": 1000 + int(np.random.rand() * 100),
                        }
                    )
            return pd.DataFrame(data)


# Optional ML scoring
try:
    from screening.watchlist_ml import score_candidates
except ImportError:
    score_candidates = None

logger = logging.getLogger("signal_engine")
logger.setLevel(logging.INFO)


def generate_signals(
    watchlist_df=None, entry_col="signal_strength", **kwargs
) -> pd.DataFrame:
    symbols = ["AAPL"]
    if (
        isinstance(watchlist_df, pd.DataFrame)
        and "symbol" in watchlist_df.columns
        and not watchlist_df.empty
    ):
        symbols = list(watchlist_df["symbol"].astype(str).unique())
    engine = SignalEngine() if SignalEngine else None
    if engine is None:
        return pd.DataFrame(
            columns=[
                "symbol",
                "side",
                "price",
                "stop_loss",
                "take_profit",
                "strategy_id",
            ]
        )
    base = engine.run(symbols)
    out = base.copy()
    out["stop_loss"] = out.get("sl_scaled", out["price"] - 1.5)
    out["take_profit"] = out.get("tp_scaled", out["price"] + 2.0)
    out["strategy_id"] = "alpha_v1"
    out["trade_type"] = "INTRADAY"
    out["timestamp"] = pd.to_datetime(out.get("timestamp"))
    out["confidence"] = out.get(entry_col, out.get("signal_strength", 0.8))
    out["quantity_hint"] = out.get("position_size", 1)
    return out[
        [
            "timestamp",
            "symbol",
            "side",
            "price",
            "stop_loss",
            "take_profit",
            "strategy_id",
            "trade_type",
            "confidence",
            "quantity_hint",
        ]
    ]


class SignalEngine:
    def __init__(
        self,
        db_dsn: Optional[str] = None,
        ml_models: Optional[Dict[str, Any]] = None,
        risk_config: Optional[Dict[str, Any]] = None,
        mode: str = "paper",
        history_window: int = 100,
    ):
        self.db_client = DBClient(dsn=db_dsn) if db_dsn else DBClient()
        self.ml_models = ml_models or {}
        default_risk = {
            "base_sl_mult": 1.0,
            "base_tp_mult": 2.0,
            "volatility_scale": True,
            "regime_multiplier": {
                "bull": {"sl": 1.0, "tp": 1.2},
                "bear": {"sl": 1.2, "tp": 0.9},
                "sideways": {"sl": 0.9, "tp": 1.0},
            },
            "drawdown_sizing": {"threshold": 0.05, "size_mult": 0.5},
            "blended_score_weights": {"rule": 0.5, "ml": 0.5},
            "min_position_size": 1,
            "max_position_size": 100,
        }
        self.risk_config = {**default_risk, **(risk_config or {})}
        self.mode = mode
        self.history_window = history_window

        # Thread-safe feedback loop
        self._feedback_lock = threading.Lock()
        self._feedback_log = "trade_feedback_log.csv"
        self._feedback_batch = int(self.risk_config.get("feedback_batch", 10))

    def fetch_ohlcv(self, symbols: List[str]) -> pd.DataFrame:
        try:
            return self.db_client.fetch_ohlcv(symbols, lookback=self.history_window)
        except Exception as e:
            logger.warning("DB fetch failed, using mock data: %s", e)
            return self._mock_data(symbols)

    def _mock_data(self, symbols: List[str]) -> pd.DataFrame:
        data = []
        for sym in symbols:
            for i in range(self.history_window):
                ts = pd.Timestamp.utcnow() - pd.Timedelta(
                    minutes=(self.history_window - i)
                )
                data.append(
                    {
                        "timestamp": ts,
                        "symbol": sym,
                        "open": 100.0 + np.random.randn(),
                        "high": 101.0 + np.random.rand(),
                        "low": 99.0 - np.random.rand(),
                        "close": 100.0 + np.random.randn(),
                        "volume": 1000 + int(np.random.rand() * 100),
                    }
                )
        return pd.DataFrame(data)

    def detect_market_regime(self, df: pd.DataFrame) -> str:
        if df is None or df.empty or "close" not in df.columns:
            return "sideways"
        returns = df["close"].pct_change().dropna()
        mean = returns.mean() if not returns.empty else 0.0
        if mean > 0.001:
            return "bull"
        if mean < -0.001:
            return "bear"
        return "sideways"

    def _volatility_relative_scale(self, df: pd.DataFrame) -> pd.Series:
        if "atr" not in df.columns:
            return pd.Series(1.0, index=df.index)
        median_atr = df["atr"].median() or 1.0
        return (df["atr"] / median_atr).fillna(1.0)

    def _dynamic_sl_tp(self, signals_df: pd.DataFrame, regime: str) -> pd.DataFrame:
        cfg = self.risk_config
        base_sl = cfg.get("base_sl_mult", 1.0)
        base_tp = cfg.get("base_tp_mult", 2.0)
        regime_entry = cfg.get("regime_multiplier", {}).get(
            regime, {"sl": 1.0, "tp": 1.0}
        )
        vol_scale = (
            self._volatility_relative_scale(signals_df)
            if cfg.get("volatility_scale", True)
            else pd.Series(1.0, index=signals_df.index)
        )
        price = signals_df.get("price", signals_df.get("close"))
        atr = signals_df.get("atr", pd.Series(1.0, index=signals_df.index))

        sl_scaled = price - (atr * base_sl * regime_entry["sl"] * vol_scale)
        tp_scaled = price + (atr * base_tp * regime_entry["tp"] * vol_scale)
        sell_mask = signals_df.get("side") == "SELL"
        sl_scaled = np.where(
            sell_mask,
            price + (atr * base_sl * regime_entry["sl"] * vol_scale),
            sl_scaled,
        )
        tp_scaled = np.where(
            sell_mask,
            price - (atr * base_tp * regime_entry["tp"] * vol_scale),
            tp_scaled,
        )

        out = signals_df.copy()
        out["sl_scaled"] = sl_scaled
        out["tp_scaled"] = tp_scaled
        out["sl_reason"] = f"base_sl={base_sl},regime_mult={regime_entry['sl']}"
        return out

    def _size_by_drawdown(
        self, signals_df: pd.DataFrame, current_drawdown: Optional[float]
    ) -> pd.DataFrame:
        cfg = self.risk_config
        min_size = cfg.get("min_position_size", 1)
        max_size = cfg.get("max_position_size", 100)
        atr = signals_df.get("atr")
        base = (
            (1.0 / atr.replace(0, 1.0)).fillna(1.0)
            if atr is not None
            else pd.Series(1.0, index=signals_df.index)
        )
        base = base / (base.max() or 1.0)
        raw_size = (base * (max_size - min_size) + min_size).round().astype(int)
        dd_cfg = cfg.get("drawdown_sizing", {})
        if current_drawdown is not None and current_drawdown >= dd_cfg.get(
            "threshold", 0.05
        ):
            raw_size = (
                (raw_size * dd_cfg.get("size_mult", 0.5))
                .clip(lower=min_size)
                .astype(int)
            )
        out = signals_df.copy()
        out["position_size"] = raw_size
        return out

    def _blend_scores_and_explain(self, signals_df: pd.DataFrame) -> pd.DataFrame:
        cfg = self.risk_config
        w_rule = cfg.get("blended_score_weights", {}).get("rule", 0.5)
        w_ml = cfg.get("blended_score_weights", {}).get("ml", 0.5)
        if "signal_strength" not in signals_df.columns:
            signals_df["signal_strength"] = 0.5
        rule_s = signals_df["signal_strength"].fillna(0.5).astype(float)
        ml_s = (
            signals_df.get("ml_score", pd.Series(0.5, index=signals_df.index))
            .fillna(0.5)
            .astype(float)
        )
        blended = (w_rule * rule_s + w_ml * ml_s) / (w_rule + w_ml)
        out = signals_df.copy()
        out["blended_score"] = blended.clip(0.0, 1.0)

        def _mk_reason(row):
            return f"rule={row.get('signal_strength', 0.5):.3f} | ml={row.get('ml_score', 0.5):.3f} | blended={row.get('blended_score'):.3f} | side={row.get('side')} | price={row.get('price')}"

        out["reason"] = out.apply(_mk_reason, axis=1)
        return out

    def run(
        self, symbols: List[str], current_drawdown: Optional[float] = None, **kwargs
    ) -> pd.DataFrame:
        ohlcv_df = self.fetch_ohlcv(symbols)
        regime = self.detect_market_regime(ohlcv_df)
        if "ema_fast" not in ohlcv_df.columns and "close" in ohlcv_df.columns:
            ohlcv_df["ema_fast"] = ohlcv_df["close"].ewm(span=9, adjust=False).mean()
        if "ema_slow" not in ohlcv_df.columns and "close" in ohlcv_df.columns:
            ohlcv_df["ema_slow"] = ohlcv_df["close"].ewm(span=21, adjust=False).mean()

        try:
            signals_df = generate_signals(
                ohlcv_df, mode=self.mode, regime=regime, **kwargs
            )
        except Exception as e:
            logger.exception("generate_signals failed: %s", e)
            return pd.DataFrame()

        if signals_df is None or signals_df.empty:
            return signals_df

        if self.ml_models and score_candidates is not None:
            try:
                proba_cols = [
                    score_candidates(signals_df, model)["proba"]
                    for model in self.ml_models.values()
                ]
                if proba_cols:
                    signals_df["ml_score"] = np.mean(proba_cols, axis=0)
            except Exception as e:
                logger.warning("ML scoring failed: %s", e)

        signals_df = self._dynamic_sl_tp(signals_df, regime)
        signals_df = self._size_by_drawdown(signals_df, current_drawdown)
        signals_df = self._blend_scores_and_explain(signals_df)
        signals_df = self.filter_noise(signals_df)
        signals_df = self.adjust_for_risk(signals_df)
        signals_df["engine_mode"] = self.mode
        signals_df["regime"] = regime
        return signals_df.reset_index(drop=True)

    def filter_noise(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df
        if "atr" in df.columns:
            out = out[out["atr"] > df["atr"].median()]
        if "volume" in df.columns:
            out = out[out["volume"] > df["volume"].median()]
        return out

    def adjust_for_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        max_drawdown = self.risk_config.get("max_drawdown")
        if max_drawdown and self.risk_config.get("recent_loss_rate", 0) > 0.5:
            if "signal_strength" in df.columns:
                df = df.copy()
                df["signal_strength"] *= 0.5
        return df

    def register_trade_result(
        self,
        trade_id: str,
        pnl: float,
        sl_hit: bool,
        tp_hit: bool,
        meta: Optional[Dict[str, Any]] = None,
    ):
        meta = meta or {}
        row = {
            "trade_id": trade_id,
            "pnl": float(pnl),
            "sl_hit": bool(sl_hit),
            "tp_hit": bool(tp_hit),
            **{f"meta_{k}": v for k, v in meta.items()},
        }
        with self._feedback_lock:
            if os.path.exists(self._feedback_log):
                try:
                    df = pd.read_csv(self._feedback_log)
                except Exception:
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            try:
                df.to_csv(self._feedback_log, index=False)
            except Exception as e:
                logger.warning("Failed to persist feedback log: %s", e)

            try:
                if len(df) >= max(1, self._feedback_batch):
                    recent = df.tail(self._feedback_batch)
                    loss_rate = (recent["pnl"] < 0).mean()
                    cfg = self.risk_config
                    if loss_rate > 0.6:
                        cfg["base_sl_mult"] = max(
                            0.2, cfg.get("base_sl_mult", 1.0) * 0.9
                        )
                        cfg["base_tp_mult"] = cfg.get("base_tp_mult", 2.0) * 1.05
                        logger.info("Auto-tune: tightened SL, stretched TP")
                    elif loss_rate < 0.3:
                        cfg["base_sl_mult"] = cfg.get("base_sl_mult", 1.0) * 1.02
                        cfg["base_tp_mult"] = max(
                            1.0, cfg.get("base_tp_mult", 2.0) * 0.98
                        )
                        logger.info("Auto-tune: loosened SL, reduced TP")
            except Exception as e:
                logger.exception("Auto-tune failed: %s", e)
