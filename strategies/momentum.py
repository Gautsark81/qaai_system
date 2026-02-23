# strategies/momentum.py
"""
Supercharged Momentum Strategy for AMATS / QAAI

Features:
- Reads OHLCV from sqlite via injected deps["db_ohlcv"] (SQLiteClient)
- Computes indicators: EMA, ATR, RSI, Momentum
- Generates signals with score/confidence
- Position sizing using Kelly fraction combined with ATR scaling
- Risk checks: max position size, recent losses cool-down, symbol blacklist
- Async + sync interfaces (generate_signals, generate_signals_async)
- Deterministic RNG via deps["rng"] (optional)
- Clear typing and safe numeric handling

Usage:
    from strategies.registry import get_deps
    deps = get_deps()
    strat = MomentumStrategy(deps, config={...})
    signals = strat.generate_signals(snapshot)

Design notes:
- Strategy is pure-signal generator (no execution), returns list of dicts:
    {
        "symbol": "AAPL",
        "side": "buy" | "sell",
        "size": 10.0,            # suggested contract/qty
        "score": 0.123,         # relative score
        "confidence": 0.8,      # [0..1]
        "meta": {...}
    }
"""

from __future__ import annotations
import math
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Iterable, List, Optional
from datetime import datetime

import pandas as pd
import numpy as np

LOGGER = logging.getLogger("strategies.momentum")


@dataclass
class MomentumConfig:
    lookback: int = 30
    signal_window: int = 20
    ema_short: int = 12
    ema_long: int = 26
    atr_window: int = 14
    rsi_window: int = 14
    min_confidence: float = 0.15
    max_position_pct: float = 0.05  # max fraction of account equity per trade
    kelly_fraction: float = 0.25  # fraction of Kelly to use
    atr_scale: float = 1.0  # multiplier for ATR when sizing
    cooldown_minutes: int = 30  # skip signals after recent stoploss for symbol
    blacklist: Iterable[str] = field(default_factory=list)


class MomentumStrategy:
    def __init__(self, deps: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        """
        deps expected keys:
          - db_ohlcv: SQLiteClient-like with fetchall(query, params)
          - db_preds: optional, for reading predictions
          - logger: optional logger
          - rng: optional numpy rng
          - account: dict with 'equity' (float) for sizing (optional)
          - risk: optional risk manager interface with `recent_losses(symbol, minutes)` method
        """
        self.deps = deps
        self.config = MomentumConfig(**(config or {}))
        self.logger = deps.get("logger", LOGGER)
        self.rng = deps.get("rng", np.random.default_rng(0))
        self.account = deps.get("account", {"equity": 100000.0})  # default equity
        self.db = deps["db_ohlcv"]

    # ---------------------------
    # Indicator helpers (pandas expected)
    # ---------------------------
    @staticmethod
    def ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def atr(df: pd.DataFrame, n: int) -> pd.Series:
        """Calculate ATR from a DataFrame with columns: high, low, close"""
        high = df["high"]
        low = df["low"]
        close = df["close"].shift(1)
        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(n, min_periods=1).mean()

    @staticmethod
    def rsi(series: pd.Series, n: int) -> pd.Series:
        delta = series.diff()
        up = delta.clip(lower=0.0)
        down = -1 * delta.clip(upper=0.0)
        ma_up = up.ewm(alpha=1 / n, min_periods=n).mean()
        ma_down = down.ewm(alpha=1 / n, min_periods=n).mean()
        rs = ma_up / (ma_down.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    @staticmethod
    def momentum(closes: pd.Series, period: int) -> pd.Series:
        return closes.pct_change(periods=period)

    # ---------------------------
    # Data loading
    # ---------------------------
    def load_ohlcv(self, symbol: str, limit: int) -> pd.DataFrame:
        q = "SELECT ts, open, high, low, close, volume FROM ohlcv WHERE symbol=? ORDER BY ts DESC LIMIT ?"
        rows = self.db.fetchall(q, (symbol, limit))
        if not rows:
            return pd.DataFrame()
        # Convert sqlite3.Row objects to list of dicts so pandas gets correct columns
        list_of_dicts = [dict(r) for r in rows]
        df = pd.DataFrame.from_records(list_of_dicts)
        # Make sure columns are in expected order and types
        df = df[["ts", "open", "high", "low", "close", "volume"]]
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        # reverse chronological order to chronological
        df = df.iloc[::-1].reset_index(drop=True)
        return df

    # ---------------------------
    # Risk checks & sizing
    # ---------------------------
    def recent_stoploss_cooldown(self, symbol: str) -> bool:
        """Ask risk manager (if present) if symbol had recent stoplosses."""
        risk = self.deps.get("risk")
        if risk and hasattr(risk, "recent_losses"):
            recent = risk.recent_losses(symbol, self.config.cooldown_minutes)
            if recent and recent > 0:
                self.logger.debug(
                    "Symbol %s in cooldown due to %d recent losses", symbol, recent
                )
                return True
        return False

    def compute_size(self, stop_atr: float, side: str) -> float:
        """
        Size = min(max_position_pct * equity, kelly_fraction * kelly_amount_scaled_by_atr)
        Kelly approximated with score -> but for safety we use configured kelly_fraction.
        stop_atr: ATR in price units (absolute)
        """
        equity = float(self.account.get("equity", 100000.0))
        max_size_value = equity * self.config.max_position_pct

        # conservative Kelly: assume edge = 0.02 (2%) and win_loss ~ 1:1 default -> kelly = edge / var
        # To keep it safe, we use configured kelly_fraction
        kelly_risk_value = equity * (
            self.config.kelly_fraction * 0.02
        )  # conservative proportional value
        # scale by ATR so that volatile instruments get smaller position in price terms:
        if stop_atr <= 0 or math.isnan(stop_atr):
            size_by_atr = kelly_risk_value
        else:
            # translate risk value to qty using price ~ 1 for base; caller should adjust for lot size if needed
            size_by_atr = kelly_risk_value / (stop_atr * self.config.atr_scale)

        size = min(max_size_value, size_by_atr)
        # ensure size is positive and not tiny
        if math.isnan(size) or size <= 0:
            return 0.0
        return float(max(0.0, round(size, 6)))

    # ---------------------------
    # Core signal generation (sync)
    # ---------------------------
    def generate_signals(
        self, symbol_list: Iterable[str], snapshot: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate signals for a list of symbols.
        snapshot: optional market snapshot or context (not required)
        """
        signals: List[Dict[str, Any]] = []
        for symbol in symbol_list:
            if symbol in (self.config.blacklist or []):
                self.logger.debug("Skipping blacklisted symbol %s", symbol)
                continue

            # risk cooldown
            if self.recent_stoploss_cooldown(symbol):
                continue

            df = self.load_ohlcv(symbol, limit=self.config.lookback + 5)
            if df.empty or len(df) < max(self.config.lookback, self.config.ema_long):
                self.logger.debug(
                    "Insufficient data for %s: have %d rows", symbol, len(df)
                )
                continue

            close = df["close"]

            # indicators
            ema_short = self.ema(close, self.config.ema_short)
            ema_long = self.ema(close, self.config.ema_long)
            mom = self.momentum(close, self.config.signal_window).iloc[
                -1
            ]  # latest momentum %
            atr_series = self.atr(df, self.config.atr_window)
            atr_latest = float(atr_series.iloc[-1] if not atr_series.empty else np.nan)
            rsi_series = self.rsi(close, self.config.rsi_window)
            rsi_latest = float(rsi_series.iloc[-1] if not rsi_series.empty else 50.0)

            # signal logic: EMA crossover + momentum confirmation + RSI filter
            ema_cross = ema_short.iloc[-1] - ema_long.iloc[-1]
            trend = "bull" if ema_cross > 0 else "bear"
            score = float(mom) if not math.isnan(mom) else 0.0

            # confidence: combine normalized momentum and RSI-based moderation
            conf_mom = min(1.0, abs(score) * 5)  # scale factor
            conf_rsi = 1.0
            # avoid overbought/oversold extremes for entries
            if (rsi_latest > 80 and score > 0) or (rsi_latest < 20 and score < 0):
                conf_rsi = 0.2
            confidence = float(conf_mom * conf_rsi)

            # apply min confidence threshold
            if confidence < self.config.min_confidence:
                self.logger.debug("Low confidence for %s: %f", symbol, confidence)
                continue

            side = "buy" if score > 0 else "sell"
            # compute suggested size using ATR as stop distance
            size = self.compute_size(stop_atr=atr_latest, side=side)

            if size <= 0:
                self.logger.debug(
                    "Computed zero size for %s (atr=%s)", symbol, atr_latest
                )
                continue

            signal = {
                "symbol": symbol,
                "side": side,
                "size": size,
                "score": score,
                "confidence": confidence,
                "meta": {
                    "ema_short": float(ema_short.iloc[-1]),
                    "ema_long": float(ema_long.iloc[-1]),
                    "atr": float(atr_latest),
                    "rsi": float(rsi_latest),
                    "trend": trend,
                    "ts": datetime.utcnow().isoformat(),
                },
            }
            signals.append(signal)

        # sort signals by absolute score descending (higher priority first)
        signals = sorted(signals, key=lambda s: abs(s["score"]), reverse=True)
        return signals

    # ---------------------------
    # Async wrapper
    # ---------------------------
    async def generate_signals_async(
        self, symbol_list: Iterable[str], snapshot: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        # in an async environment, simply run the sync version; strategy logic is IO-bound on sqlite,
        # so if you move to an async DB client, implement true async here.
        return self.generate_signals(symbol_list, snapshot)

    # ---------------------------
    # Utility: health check
    # ---------------------------
    def health_check(self) -> Dict[str, Any]:
        # quick self-check returning config and last-known equity
        return {
            "name": "MomentumStrategy",
            "configured_lookback": self.config.lookback,
            "account_equity": self.account.get("equity"),
            "rng_present": self.rng is not None,
        }


# Optional registry helper: for frameworks that auto-discover strategies
def register(
    deps: Dict[str, Any], config: Optional[Dict[str, Any]] = None
) -> MomentumStrategy:
    return MomentumStrategy(deps, config=config)
