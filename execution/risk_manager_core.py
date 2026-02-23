# execution/risk_manager_core.py
from __future__ import annotations

import time
import logging
from typing import Dict, Any, Optional, Tuple

log = logging.getLogger("RiskManagerCore")


class RiskLimitViolation(Exception):
    pass


class RiskManagerCore:
    """
    Phase-B Canonical Risk Engine

    Golden Rules:
    - Decides risk ONLY
    - No execution
    - No routing
    - Deterministic
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # ---- Kill switch ----
        self._kill_switch = False
        self._kill_reason = None

        # ---- Drawdown tracking ----
        self._peak_equity: Optional[float] = None
        self._current_equity: Optional[float] = None
        self.max_drawdown_pct = self.config.get("max_drawdown_pct")

        # ---- Exposure tracking ----
        self.active_trades: Dict[str, Dict[str, Any]] = {}

    # =========================
    # Kill switch
    # =========================
    def trigger_kill_switch(self, reason: str):
        self._kill_switch = True
        self._kill_reason = reason
        log.warning("KILL_SWITCH_ACTIVE (%s)", reason)

    def kill_switch_active(self) -> bool:
        return self._kill_switch

    def circuit_reason(self) -> str:
        if self._kill_switch:
            return "KillSwitch: KILL_SWITCH_ACTIVE"
        if self.circuit_breaker_tripped():
            return "CircuitBreaker: DRAWDOWN"
        return ""

    # =========================
    # Equity & drawdown
    # =========================
    def heartbeat(self, account_equity: float):
        self._current_equity = account_equity
        if self._peak_equity is None:
            self._peak_equity = account_equity
        else:
            self._peak_equity = max(self._peak_equity, account_equity)

    def circuit_breaker_tripped(self) -> bool:
        if (
            self.max_drawdown_pct is None
            or self._peak_equity is None
            or self._current_equity is None
        ):
            return False

        dd = (self._peak_equity - self._current_equity) / self._peak_equity * 100
        return dd > self.max_drawdown_pct

    def is_trading_allowed(self, account_equity: Optional[float] = None) -> bool:
        if self._kill_switch:
            return False
        if account_equity is not None:
            self.heartbeat(account_equity)
        return not self.circuit_breaker_tripped()

    # =========================
    # Risk evaluation
    # =========================
    def evaluate_risk(
        self, order: Dict[str, Any], account_equity: Optional[float]
    ) -> Tuple[bool, str]:
        if not self.is_trading_allowed(account_equity):
            return False, self.circuit_reason()

        qty = order.get("quantity") or order.get("qty", 0)
        price = order.get("price", 0)

        # simple sanity
        if qty <= 0 or price <= 0:
            return False, "Invalid order size"

        return True, "OK"

    # =========================
    # Trade lifecycle
    # =========================
    def update_trade_log(self, trade: Dict[str, Any]):
        oid = trade.get("order_id")
        if not oid:
            return

        status = trade.get("status")
        if status in {"open", "OPEN"}:
            self.active_trades[oid] = trade
        elif status in {"closed", "FILLED", "CANCELLED"}:
            self.active_trades.pop(oid, None)
