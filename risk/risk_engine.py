# path: risk/risk_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

# FIXED: use relative imports instead of qaai_system.risk.*
from .risk_limits import RiskLimits
from .risk_state import RiskState
from .risk_exceptions import (
    RiskError,
    HardRiskLimitBreach,
    SoftRiskLimitBreach,
    CircuitBreakerTripped,
)

PortfolioLike = Union[Dict[str, Any], Any]


@dataclass
class OrderRiskResult:
    allowed: bool
    hard_breaches: List[str]
    soft_breaches: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "hard_breaches": list(self.hard_breaches),
            "soft_breaches": list(self.soft_breaches),
        }


class RiskEngine:
    """
    RiskEngine v1.5

    Responsibilities:
    - Track daily PnL and kill switch (hard risk)
    - Evaluate new orders against configured RiskLimits
      using the current PortfolioState
    - Handle per-strategy daily loss limits
    - Handle intraday equity drawdown from start-of-day equity
    - Expose manual kill/clear controls
    """

    def __init__(
        self,
        limits: Optional[RiskLimits] = None,
        state: Optional[RiskState] = None,
        logger: Optional[Any] = None,
    ) -> None:
        self.limits = limits or RiskLimits()
        self.state = state or RiskState()
        self.logger = logger

    # ------------------------------------------------------------------
    # Helpers to read PortfolioState-like data
    # ------------------------------------------------------------------
    def _get_equity(self, portfolio: PortfolioLike) -> Optional[float]:
        if portfolio is None:
            return None
        if isinstance(portfolio, dict):
            return portfolio.get("equity")
        return getattr(portfolio, "equity", None)

    def _get_realized_pnl(self, portfolio: PortfolioLike) -> float:
        if portfolio is None:
            return 0.0
        if isinstance(portfolio, dict):
            return float(portfolio.get("realized_pnl", 0.0) or 0.0)
        return float(getattr(portfolio, "realized_pnl", 0.0) or 0.0)

    def _get_positions(self, portfolio: PortfolioLike) -> Dict[str, Dict[str, Any]]:
        if portfolio is None:
            return {}
        if isinstance(portfolio, dict):
            return portfolio.get("positions", {}) or {}
        return getattr(portfolio, "positions", {}) or {}

    def _get_exposures(
        self,
        portfolio: PortfolioLike,
    ) -> Tuple[float, float]:
        """
        Compute gross and net exposure from positions.

        Assumes each position dict has:
            - quantity
            - avg_price
            - side in {"LONG","SHORT"} (optional; sign by quantity if missing)
        """
        positions = self._get_positions(portfolio)
        gross = 0.0
        net = 0.0
        for _, p in positions.items():
            qty = float(p.get("quantity", 0.0) or 0.0)
            price = float(p.get("avg_price", 0.0) or 0.0)
            side = str(p.get("side", "")).upper()
            notional = abs(qty) * price
            if notional <= 0:
                continue
            gross += notional
            if side == "SHORT":
                net -= notional
            else:
                net += notional
        return gross, net

    def _log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Structured risk event logging.

        Example shapes:
            {"type": "RISK_BLOCKED_ORDER", ...}
            {"type": "RISK_KILL_SWITCH", ...}
        """
        if not self.logger:
            return
        try:
            event = {"type": event_type, **payload}
            # Use info-level for high-level events
            if hasattr(self.logger, "info"):
                self.logger.info(event)
        except Exception:
            # Logging is best-effort only
            pass

    # ------------------------------------------------------------------
    # Manual kill / clear
    # ------------------------------------------------------------------
    def set_kill_switch(self, reason: str = "MANUAL_KILL") -> None:
        self.state.kill_switch = True
        self.state.kill_reason = reason
        self._log_event(
            "RISK_KILL_SWITCH",
            {
                "reason": reason,
                "trading_date": self.state.trading_date,
            },
        )

    def clear_kill_switch(self, reason: str = "MANUAL_CLEAR") -> None:
        self.state.kill_switch = False
        self.state.kill_reason = None
        self._log_event(
            "RISK_KILL_SWITCH_CLEARED",
            {
                "reason": reason,
                "trading_date": self.state.trading_date,
            },
        )

    # ------------------------------------------------------------------
    # Trading allowed? (kill-switch / daily limits / drawdown)
    # ------------------------------------------------------------------
    def is_trading_allowed(self, portfolio: Optional[PortfolioLike] = None) -> bool:
        equity = self._get_equity(portfolio)
        self.state.maybe_rollover(current_equity=equity)

        # HARD KILL SWITCH — once tripped, trading is always disallowed
        # (test-locked behavior)
        if self.state.kill_switch:
            return False

        # Hard kill-switch
        if self.state.kill_switch:
            return False

        realized_pnl = self._get_realized_pnl(portfolio) + self.state.cumulative_realized_pnl

        # Hard daily loss (absolute)
        if self.limits.max_daily_loss is not None:
            if realized_pnl <= -abs(self.limits.max_daily_loss):
                return False

        # Hard daily loss (% of equity)
        if equity and self.limits.max_daily_loss_pct is not None:
            max_loss_abs = -abs(self.limits.max_daily_loss_pct) * float(equity)
            if realized_pnl <= max_loss_abs:
                return False

        # Intraday drawdown from start-of-day equity
        if (
            equity is not None
            and self.state.start_of_day_equity is not None
            and self.limits.max_intraday_drawdown_pct is not None
        ):
            sod = float(self.state.start_of_day_equity)
            if sod > 0:
                drawdown = (float(equity) - sod) / sod
                if drawdown <= -abs(self.limits.max_intraday_drawdown_pct):
                    return False

        return True

    def ensure_trading_allowed(self, portfolio: Optional[PortfolioLike] = None) -> None:
        if not self.is_trading_allowed(portfolio):
            if not self.state.kill_switch:
                # If state didn't already set a reason, pick a generic one
                if self.state.kill_reason is None:
                    self.state.kill_reason = "DAILY_LOSS_LIMIT"
                self.state.kill_switch = True
            raise CircuitBreakerTripped(
                f"Trading disabled by RiskEngine (reason={self.state.kill_reason})"
            )

    # ------------------------------------------------------------------
    # Order evaluation
    # ------------------------------------------------------------------
    def evaluate_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        portfolio: Optional[PortfolioLike] = None,
    ) -> OrderRiskResult:
        """
        Evaluate if a *new* order is allowed given the portfolio and limits.

        Returns an OrderRiskResult with hard/soft breaches, but does not
        raise. Caller can decide whether to block.
        """
        equity = self._get_equity(portfolio)
        self.state.maybe_rollover(current_equity=equity)

        hard: List[str] = []
        soft: List[str] = []

        eq = equity or 0.0
        positions = self._get_positions(portfolio)
        gross_exp, net_exp = self._get_exposures(portfolio)

        # Compute order notional
        notional = abs(float(quantity) * float(price))

        # --- Order-level limits ---
        if (
            self.limits.max_order_notional_value is not None
            and notional > self.limits.max_order_notional_value
        ):
            hard.append(
                f"ORDER_NOTIONAL>{self.limits.max_order_notional_value} ({notional:.2f})"
            )

        if (
            eq > 0
            and self.limits.max_order_notional_pct is not None
            and (notional / eq) > self.limits.max_order_notional_pct
        ):
            hard.append(
                f"ORDER_NOTIONAL_PCT>{self.limits.max_order_notional_pct:.4f}"
            )

        # --- Symbol weight ---
        if eq > 0 and self.limits.max_symbol_weight is not None:
            existing = positions.get(symbol, {})
            existing_qty = float(existing.get("quantity", 0.0) or 0.0)
            existing_price = float(existing.get("avg_price", price) or price)
            existing_notional = abs(existing_qty * existing_price)

            new_total_symbol_exposure = existing_notional + notional
            weight = new_total_symbol_exposure / eq
            if weight > self.limits.max_symbol_weight:
                hard.append(
                    f"SYMBOL_WEIGHT>{self.limits.max_symbol_weight:.4f} ({weight:.4f})"
                )

        # --- Portfolio exposures ---
        new_gross = gross_exp + notional
        new_net = net_exp
        if side.upper() == "SELL":
            new_net -= notional
        else:
            new_net += notional

        if eq > 0 and self.limits.max_gross_exposure_pct is not None:
            if (new_gross / eq) > self.limits.max_gross_exposure_pct:
                hard.append(
                    f"GROSS_EXPOSURE>{self.limits.max_gross_exposure_pct:.4f}"
                )

        if eq > 0 and self.limits.max_net_exposure_pct is not None:
            if abs(new_net / eq) > self.limits.max_net_exposure_pct:
                hard.append(
                    f"NET_EXPOSURE>{self.limits.max_net_exposure_pct:.4f}"
                )

        # --- Max open positions (distinct symbols) ---
        if self.limits.max_open_positions is not None:
            open_syms = {
                s
                for s, p in positions.items()
                if (p.get("quantity", 0) or 0) != 0
            }
            if symbol not in open_syms and len(open_syms) >= self.limits.max_open_positions:
                hard.append(
                    f"OPEN_POSITIONS>{self.limits.max_open_positions}"
                )

        allowed = len(hard) == 0

        if not allowed:
            self.state.num_blocked_orders += 1
            self._log_event(
                "RISK_BLOCKED_ORDER",
                {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "hard_breaches": list(hard),
                    "soft_breaches": list(soft),
                    "equity": eq,
                },
            )

        if self.logger:
            try:
                self.logger.debug(
                    "RiskEngine.evaluate_order: symbol=%s side=%s qty=%s price=%.4f "
                    "equity=%.2f notional=%.2f allowed=%s hard=%s soft=%s",
                    symbol,
                    side,
                    quantity,
                    price,
                    eq,
                    notional,
                    allowed,
                    hard,
                    soft,
                )
            except Exception:
                pass

        return OrderRiskResult(allowed=allowed, hard_breaches=hard, soft_breaches=soft)

    # ------------------------------------------------------------------
    # Fill / PnL updates
    # ------------------------------------------------------------------
    def register_fill(
        self,
        realized_pnl: float,
        fees: float = 0.0,
        portfolio: Optional[PortfolioLike] = None,
        strategy_id: Optional[str] = None,
    ) -> None:
        """
        Update risk state after a trade is closed or partially realized.

        Parameters
        ----------
        realized_pnl : float
            Realized PnL for this fill.
        fees : float, optional
            Fees associated with this fill.
        portfolio : PortfolioLike, optional
            Current portfolio view (for equity, realized_pnl).
        strategy_id : str, optional
            Strategy identifier for strategy-specific daily limits.
        """
        equity = self._get_equity(portfolio)
        self.state.maybe_rollover(current_equity=equity)

        pnl = float(realized_pnl)
        self.state.cumulative_realized_pnl += pnl
        self.state.cumulative_fees += float(fees)
        self.state.num_trades += 1

        # Per-strategy PnL
        if strategy_id:
            current = self.state.per_strategy_realized_pnl.get(strategy_id, 0.0)
            self.state.per_strategy_realized_pnl[strategy_id] = current + pnl

        # Aggregate realized PnL from portfolio + internal state
        total_realized = self._get_realized_pnl(portfolio) + self.state.cumulative_realized_pnl
        eq = float(equity) if equity is not None else None

        # ----- Global daily loss limits -----
        reason: Optional[str] = None

        if self.limits.max_daily_loss is not None:
            if total_realized <= -abs(self.limits.max_daily_loss):
                reason = "DAILY_LOSS_ABS"

        if (
            reason is None
            and eq is not None
            and self.limits.max_daily_loss_pct is not None
        ):
            max_loss_abs = -abs(self.limits.max_daily_loss_pct) * eq
            if total_realized <= max_loss_abs:
                reason = "DAILY_LOSS_PCT"

        # ----- Strategy-specific daily loss limits -----
        if reason is None and strategy_id:
            # Absolute per-strategy limit
            abs_lim = self.limits.max_strategy_daily_loss.get(strategy_id)
            if abs_lim is not None:
                if self.state.per_strategy_realized_pnl.get(strategy_id, 0.0) <= -abs(abs_lim):
                    reason = "STRATEGY_DAILY_LOSS"

            # Percentage per-strategy limit (vs equity)
            pct_lim = self.limits.max_strategy_daily_loss_pct.get(strategy_id)
            if reason is None and eq is not None and pct_lim is not None:
                max_loss_abs = -abs(pct_lim) * eq
                if self.state.per_strategy_realized_pnl.get(strategy_id, 0.0) <= max_loss_abs:
                    reason = "STRATEGY_DAILY_LOSS_PCT"

        # ----- Intraday drawdown -----
        if (
            reason is None
            and eq is not None
            and self.state.start_of_day_equity is not None
            and self.limits.max_intraday_drawdown_pct is not None
        ):
            sod = float(self.state.start_of_day_equity)
            if sod > 0:
                drawdown = (eq - sod) / sod
                if drawdown <= -abs(self.limits.max_intraday_drawdown_pct):
                    reason = "DAILY_DRAWDOWN"

        if reason is not None:
            self.state.kill_switch = True
            self.state.kill_reason = reason


            # IMPORTANT:
            # Once kill switch is tripped via fill,
            # trading must be immediately disallowed,
            # regardless of portfolio snapshot lag.
            # (tests assert this)

            self._log_event(
                "RISK_KILL_SWITCH",
                {
                    "reason": reason,
                    "equity": eq,
                    "total_realized_pnl": total_realized,
                    "strategy_id": strategy_id,
                    "trading_date": self.state.trading_date,
                },
            )

        if self.logger:
            try:
                self.logger.debug(
                    "RiskEngine.register_fill: realized_pnl=%.2f fees=%.2f "
                    "cum_pnl=%.2f kill_switch=%s reason=%s",
                    pnl,
                    fees,
                    self.state.cumulative_realized_pnl,
                    self.state.kill_switch,
                    self.state.kill_reason,
                )
            except Exception:
                pass
