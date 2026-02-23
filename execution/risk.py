# qaai_system/execution/risk.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

from .base import ExecutionProvider


@dataclass
class RiskLimits:
    max_gross_exposure: float = 1.0  # fraction of NAV
    max_symbol_weight: float = 0.25  # fraction of NAV per symbol
    max_order_notional: float = 1e9  # absolute notional cap
    price_band_bps: float = 100.0
    daily_loss_limit: float = 0.05  # fraction of NAV
    max_open_orders: int = 100
    kill_switch: bool = False  # config toggle


class RiskManager:
    """
    Performs pre-trade checks and exposes kill-switch behavior.
    Uses the execution provider for current positions/prices/account.
    """

    def __init__(
        self,
        limits: RiskLimits,
        provider: ExecutionProvider,
        kill_file: Optional[str] = None,
    ):
        self.limits = limits
        self.provider = provider
        self.kill_file = kill_file

    def is_kill_switch_armed(self) -> bool:
        if self.limits.kill_switch:
            return True
        if self.kill_file and Path(self.kill_file).exists():
            return True
        return False

    def pre_trade_check(self, plan: Dict[str, Any], mid_price: Optional[float] = None):
        """
        Validate the plan against risk limits.
        Raises RuntimeError for kill switch, ValueError for specific risk blocks (RISK_BLOCK: code)
        """
        if self.is_kill_switch_armed():
            raise RuntimeError("KILL_SWITCH_ACTIVE")

        symbol = plan.get("symbol")
        qty = int(plan.get("qty", 0))
        if qty <= 0:
            return True  # nothing to do for zero-sized plans

        side = str(plan.get("side", "buy")).lower()

        # determine price
        if mid_price is None:
            mid_price = self.provider.get_last_price(symbol) or 0.0
        mid_price = float(mid_price or 0.0)

        # account / NAV
        account = self.provider.get_account() or {}
        nav = float(account.get("nav", 1.0) or 1.0)

        # notional check
        notional = qty * mid_price
        if (
            self.limits.max_order_notional is not None
            and notional > self.limits.max_order_notional
        ):
            self._check(False, "order_notional_cap")

        # open orders limit
        try:
            open_count = len(self.provider.get_open_orders())
        except Exception:
            open_count = 0
        if (
            self.limits.max_open_orders is not None
            and open_count >= self.limits.max_open_orders
        ):
            self._check(False, "too_many_open_orders")

        # symbol cap check
        positions = self.provider.get_positions() or {}
        cur_qty = int(positions.get(symbol, 0) or 0)
        future_qty = cur_qty + (qty if side == "buy" else -qty)
        if abs(future_qty) * mid_price > (self.limits.max_symbol_weight * nav):
            self._check(False, "symbol_cap")

        # gross exposure (approx): sum abs(q)*last_price + new notional
        gross = 0.0
        for s, q in positions.items():
            # q is int qty; try to get a last price from provider
            p = self.provider.get_last_price(s) or mid_price or 0.0
            gross += abs(int(q)) * float(p)
        gross += abs(qty) * mid_price
        if gross > (self.limits.max_gross_exposure * nav):
            self._check(False, "gross_exposure")

        return True

    def cancel_all_open_orders(self) -> int:
        """
        Cancel all open child orders via provider; returns number canceled.
        """
        canceled = 0
        try:
            open_ids = self.provider.get_open_orders()
        except Exception:
            open_ids = []
        for oid in open_ids:
            try:
                ok = self.provider.cancel_order(oid)
                if ok:
                    canceled += 1
            except Exception:
                pass
        return canceled

    def _check(self, cond: bool, code: str):
        if not cond:
            raise ValueError(f"RISK_BLOCK: {code}")
