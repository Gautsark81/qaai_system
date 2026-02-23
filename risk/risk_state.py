# path: qaai_system/risk/risk_state.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional


def _today_str() -> str:
    return date.today().isoformat()


@dataclass
class RiskState:
    """
    Mutable per-day risk state.

    Can be stored and restored between runs if needed.
    """

    trading_date: str = field(default_factory=_today_str)
    cumulative_realized_pnl: float = 0.0
    cumulative_fees: float = 0.0
    num_trades: int = 0
    num_blocked_orders: int = 0

    # Start-of-day equity for drawdown calculation
    start_of_day_equity: Optional[float] = None

    # Per-strategy realized PnL (absolute)
    per_strategy_realized_pnl: Dict[str, float] = field(default_factory=dict)

    # Circuit breaker state
    kill_switch: bool = False
    kill_reason: Optional[str] = None

    def maybe_rollover(
        self,
        current_date: Optional[str] = None,
        current_equity: Optional[float] = None,
    ) -> None:
        """
        Reset daily counters when the date changes.
        Also initialize start_of_day_equity if we have it.
        """
        current_date = current_date or _today_str()
        if current_date != self.trading_date:
            self.trading_date = current_date
            self.cumulative_realized_pnl = 0.0
            self.cumulative_fees = 0.0
            self.num_trades = 0
            self.num_blocked_orders = 0
            self.per_strategy_realized_pnl.clear()
            self.kill_switch = False
            self.kill_reason = None
            self.start_of_day_equity = current_equity
        else:
            # Same date; if SoD equity not set, initialize if available
            if self.start_of_day_equity is None and current_equity is not None:
                self.start_of_day_equity = current_equity
