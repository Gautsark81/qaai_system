#  execution/risk_manager.py

from __future__ import annotations

import os
import time
import datetime
from typing import Dict, Any, Optional, Tuple


# ============================================================
# Exceptions
# ============================================================

class RiskViolation(Exception):
    pass


class RiskLimitViolation(Exception):
    pass


# ============================================================
# Config containers (legacy compatible)
# ============================================================

class RiskLimits:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def as_dict(self):
        return dict(self.__dict__)


RiskConfig = RiskLimits


# ============================================================
# RiskManager (LOCKED CONTRACT)
# ============================================================

class RiskManager:
    """
    Deterministic execution-grade risk engine.

    DOMINANCE ORDER (LOCKED):
    1. Kill switch
    2. Circuit breaker
    3. Gross position sanity
    4. ATR loss
    5. Volatility regime
    6. Symbol cap (LAST)
    """

    # --------------------------------------------------------
    # INIT
    # --------------------------------------------------------
    KILL_PREFIX = "KillSwitch:"

    def __init__(self, config: Optional[Any] = None, provider=None, max_drawdown_pct=None):
        if config is not None and not isinstance(config, dict):
            config = vars(config)

        self.config = config or {}
        self.provider = provider

        self.starting_cash = float(self.config.get("starting_cash", 100_000.0))
        self.max_drawdown_pct = (
            max_drawdown_pct
            if max_drawdown_pct is not None
            else self.config.get("max_drawdown_pct")
        )

        # ---- switches ----
        self._kill_switch = bool(self.config.get("kill_switch", False))
        self.kill_switch_file = self.config.get("kill_switch_file")

        # ---- breakers ----
        self._peak_equity: Optional[float] = None
        self._breaker_tripped = False
        self._breaker_reason = ""

        # ---- limits ----
        self.daily_loss_limit = float(self.config.get("daily_loss_limit", float("inf")))
        self.max_position_size_pct = float(self.config.get("max_position_size_pct", 0.02))
        self.max_symbol_weight = float(self.config.get("max_symbol_weight", 0.20))
        self.per_symbol_limits = dict(self.config.get("per_symbol_limits", {}))
        self.max_atr_loss_pct = float(self.config.get("max_atr_loss_pct", 0.02))
        self.volatile_max_qty = int(self.config.get("volatile_max_qty", 50))

        # ---- reset / heartbeat ----
        self.reset_hour = int(self.config.get("reset_hour", 0))
        self.heartbeat_interval = float(self.config.get("heartbeat_interval", 60))
        self._last_heartbeat: Optional[float] = None
        self._last_reset_date: Optional[datetime.date] = None
        self._last_reset_hour_checked: Optional[datetime.datetime] = None

        # ---- state ----
        self.trade_history: list[Dict[str, Any]] = []
        self.active_trades: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, float] = {}
        self.reservations: Dict[str, Dict[str, Any]] = {}
        self.reservation_ttl = float(self.config.get("reservation_ttl", 60))

        # ---- hooks ----
        self.position_getter = None
        self.metrics_callback = None

    # ------------------------------------------------------------------
    # TIME HELPERS
    # ------------------------------------------------------------------
    def _now(self) -> datetime.datetime:
        return datetime.datetime.now()

    def _maybe_reset_daily(self):

        now = self._now()
        today = now.date()
        hour = now.hour
        reset_hour = self.reset_hour

        # First touch
        if self._last_reset_date is None:
            self._last_reset_date = today
            self._last_reset_hour_checked = now
            return

        # Date rollover reset
        if today != self._last_reset_date:
            self.trade_history.clear()
            self._last_reset_date = today
            self._last_reset_hour_checked = now
            return

        # Hour-based reset ONLY when crossing reset boundary
        if reset_hour is not None and self._last_reset_hour_checked is not None:
            prev = self._last_reset_hour_checked
            if prev.date() == today:
                if prev.hour < reset_hour <= hour:
                    self.trade_history.clear()
            self._last_reset_hour_checked = now

    # ============================================================
    # KILL SWITCH
    # ============================================================

    def trigger_kill_switch(self, reason: str = "KillSwitch"):
        self._kill_switch = True
        self._breaker_reason = f"{self.KILL_PREFIX}{reason}"

    def set_kill_switch(self, active: bool, reason: Optional[str] = None):
        self._kill_switch = bool(active)
        self._kill_switch_reason = reason

    def clear_kill_switch(self):
        self._kill_switch = False
        self._breaker_tripped = False
        self._breaker_reason = ""

    def kill_switch_active(self) -> bool:
        if self._kill_switch:
            return True
        if self.kill_switch_file and os.path.exists(self.kill_switch_file):
            return True
        return False

    def is_kill_switch_armed(self) -> bool:
        return self.kill_switch_active()

    # ============================================================
    # CIRCUIT BREAKER
    # ============================================================

    def heartbeat(self, account_equity: Optional[float] = None):
        self._last_heartbeat = time.time()
        if account_equity is None or self.max_drawdown_pct is None:
            return
        if self._peak_equity is None:
            self._peak_equity = account_equity
        self._peak_equity = max(self._peak_equity, account_equity)
        dd = (self._peak_equity - account_equity) / self._peak_equity * 100
        if dd >= self.max_drawdown_pct:
            self._breaker_tripped = True
            self._breaker_reason = "Drawdown limit breached"

    def circuit_breaker_tripped(self) -> bool:
        return self._breaker_tripped

    def circuit_reason(self) -> str:
        return self._breaker_reason

    def is_trading_allowed(self, account_equity: Optional[float] = None) -> bool:
        self._maybe_reset_daily()

        if self.kill_switch_active():
            return False

        # Enforce drawdown breaker here (tests rely on this)
        if account_equity is not None and self.max_drawdown_pct is not None:
            if self._peak_equity is None:
                self._peak_equity = account_equity
            self._peak_equity = max(self._peak_equity, account_equity)
            dd = (self._peak_equity - account_equity) / self._peak_equity * 100
            if dd >= self.max_drawdown_pct:
                self._breaker_tripped = True
                self._breaker_reason = "Drawdown limit breached"

        if self._breaker_tripped:
            return False

        # Daily loss limit is defined as % of STARTING CASH (tests rely on this)
        loss_limit = self.daily_loss_limit * self.starting_cash
        if abs(self.realized_today()) > loss_limit:
            self._breaker_tripped = True
            self._breaker_reason = "Daily loss limit breached"
            return False

        return True

    # ============================================================
    # TRADE LOGGING
    # ============================================================

    def update_trade_log(self, trade: Dict[str, Any]):
        oid = trade.get("order_id")
        status = trade.get("status")
        if status == "open" and oid:
            self.active_trades[oid] = trade
        if status == "closed":
            self.trade_history.append(
                {"pnl": float(trade.get("pnl", 0.0)), "timestamp": self._now()}
            )
            if oid in self.active_trades:
                del self.active_trades[oid]

    def realized_today(self) -> float:
        self._maybe_reset_daily()
        return sum(t["pnl"] for t in self.trade_history)

    def get_open_risk_exposure(self) -> float:
        return sum(
            t.get("quantity", 0) * t.get("price", 0)
            for t in self.active_trades.values()
        )

    # ============================================================
    # POSITION / RESERVATION
    # ============================================================

    def set_position(self, symbol: str, qty: float):
        self.positions[symbol] = qty

    def reserve(self, rid: str, symbol: str, qty: float):
        self.reservations[rid] = {"symbol": symbol, "qty": qty, "ts": time.time()}

    def release_reservation(self, rid: str):
        self.reservations.pop(rid, None)

    def is_allowed(self, symbol: str, qty: float) -> bool:
        current = (
            self.position_getter(symbol)
            if self.position_getter
            else self.positions.get(symbol, 0.0)
        )
        limit = self.per_symbol_limits.get(
            symbol, self.starting_cash * self.max_position_size_pct
        )
        return abs(current + qty) <= limit

    def can_place(
        self,
        symbol: str,
        qty: float,
        reservation_id: Optional[str] = None,
        auto_reserve: bool = False,
    ) -> bool:
        now = time.time()
        self.reservations = {
            k: v
            for k, v in self.reservations.items()
            if now - v["ts"] <= self.reservation_ttl
        }

        total_reserved = sum(r["qty"] for r in self.reservations.values())
        allowed = self.is_allowed(symbol, qty + total_reserved)

        if not allowed:
            if self.metrics_callback:
                self.metrics_callback("exceeds_check", {"symbol": symbol, "qty": qty})
            return False

        if auto_reserve and reservation_id:
            self.reserve(reservation_id, symbol, qty)
            if self.metrics_callback:
                self.metrics_callback(
                    "reservation.added", {"symbol": symbol, "qty": qty}
                )

        return True

    # ============================================================
    # ORDER-LEVEL RISK
    # ============================================================

    def check_symbol_cap(self, symbol, qty, price, account_equity):
        notional = qty * price
        cap = self.max_symbol_weight * account_equity
        if notional > cap:
            raise ValueError(f"Symbol cap exceeded for {symbol}")

    def evaluate_risk(
        self,
        order: Dict[str, Any],
        account_equity: float,
        regime_tag: Optional[str] = None,
    ):
        # ===== R3.3: kill switch enforced HERE =====
        if self.kill_switch_active():
            return False, "Kill switch active"

        symbol = order.get("symbol")
        qty = order.get("qty") or order.get("quantity", 0)
        price = float(order.get("price", 0.0))
        notional = qty * price

        # 1. Gross position sanity with symbol-cap dominance
        gross_cap = self.max_position_size_pct * account_equity
        symbol_cap = self.max_symbol_weight * account_equity

        # Symbol cap dominates ONLY if it is tighter
        if symbol_cap < gross_cap and notional > symbol_cap:
            return False, f"RISK_BLOCK: Symbol cap exceeded for {symbol}"

        # Otherwise gross sanity dominates
        if notional > gross_cap:
            return False, "Position too large"

        # 2. ATR loss
        atr = order.get("atr")
        if atr is not None:
            atr_loss = atr * abs(qty)
            if atr_loss > (self.max_atr_loss_pct * account_equity):
                return False, "ATR loss too large"

        # 3. Volatility regime
        regime = regime_tag or order.get("regime_tag")
        if regime == "volatile" and abs(qty) > self.volatile_max_qty:
            return False, "Volatile regime position limit"

        return True, "Risk checks passed"

    # ============================================================
    # Phase R1 — Missing APIs (DO NOT CHANGE EXISTING LOGIC)
    # ============================================================

    def circuit_break_on_drawdown(self, drawdown_pct: float):
        """
        Trip circuit breaker if drawdown exceeds configured limit.
        drawdown_pct is expected to be negative for losses.
        """
        if self.max_drawdown_pct is None:
            return
        if abs(drawdown_pct) >= self.max_drawdown_pct:
            self._breaker_tripped = True
            self._breaker_reason = "Drawdown limit breached"


    def is_heartbeat_stale(self) -> bool:
        """
        Heartbeat is stale if last heartbeat exceeds interval.
        """
        if self._last_heartbeat is None:
            return True
        return (time.time() - self._last_heartbeat) > self.heartbeat_interval


    def get_reservations(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a snapshot of current reservations.
        """
        return dict(self.reservations)

    # ============================================================
    # ORDER MANAGER HOOK
    # ============================================================

    def pre_submit(self, order: Dict[str, Any], state: Dict[str, Any]):
        symbol = order.get("symbol")
        qty = abs(order.get("qty") or order.get("quantity", 0))

        # --------------------------------------------------
        # ABSOLUTE SYMBOL CAPS (QTY-BASED, PRE-TRADE)
        # --------------------------------------------------
        symbol_caps = self.config.get("symbol_caps")
        if symbol_caps and symbol in symbol_caps:
            cap = symbol_caps[symbol]
            if qty > cap:
                raise RiskLimitViolation(
                    f"Symbol cap exceeded for {symbol}"
                )

    # ============================================================
    # DIAGNOSTICS
    # ============================================================

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "open_trades": len(self.active_trades),
            "active_symbols": list({t["symbol"] for t in self.active_trades.values()}),
            "total_exposure": self.get_open_risk_exposure(),
            "daily_pnl": self.realized_today(),
            "kill_switch": self.kill_switch_active(),
            "breaker": self._breaker_tripped,
        }

    def dump_state(self) -> Dict[str, Any]:
        return {
            "positions": dict(self.positions),
            "reservations": dict(self.reservations),
            "trade_history": list(self.trade_history),
            "max_position": self.starting_cash * self.max_position_size_pct,
            "per_symbol_limits": dict(self.per_symbol_limits),
            "breaker_reason": self._breaker_reason,
        }
