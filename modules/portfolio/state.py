from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, Optional, NewType

# -------------------------------------------------------------------
# Domain aliases (NO runtime cost, matches existing string-based repo)
# -------------------------------------------------------------------
Symbol = NewType("Symbol", str)
StrategyId = NewType("StrategyId", str)


# -------------------------------------------------------------------
# Core portfolio domain objects
# -------------------------------------------------------------------
@dataclass(frozen=True)
class Position:
    symbol: Symbol
    quantity: int
    avg_price: float
    strategy_id: StrategyId

    def notional(self, last_price: float) -> float:
        return abs(self.quantity) * last_price

    def unrealized_pnl(self, last_price: float) -> float:
        return (last_price - self.avg_price) * self.quantity


@dataclass(frozen=True)
class PortfolioSnapshot:
    """
    Immutable point-in-time snapshot of portfolio state.
    Used for:
    - audit
    - replay
    - analytics
    """
    timestamp: datetime
    positions: Dict[Symbol, Position]
    cash: float
    realized_pnl: float
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PortfolioState:
    """
    Phase 13.1 – Portfolio State Engine

    Single source of truth for:
    - Open positions
    - Cash balance
    - Realized PnL

    Explicitly does NOT contain:
    - Capital allocation logic
    - Broker / margin logic
    - Risk overrides
    """

    cash: float
    realized_pnl: float = 0.0
    positions: Dict[Symbol, Position] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Trade application (assumes RiskManager already approved the trade)
    # ------------------------------------------------------------------
    def apply_trade(
        self,
        *,
        symbol: Symbol,
        quantity: int,
        price: float,
        strategy_id: StrategyId,
    ) -> None:
        """
        Apply a filled trade to the portfolio.

        quantity:
            +ve = buy
            -ve = sell
        """
        if quantity == 0:
            return

        # Cash impact
        self.cash -= quantity * price

        existing = self.positions.get(symbol)

        # -------------------------
        # New position
        # -------------------------
        if existing is None:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_price=price,
                strategy_id=strategy_id,
            )
            return

        new_qty = existing.quantity + quantity

        # -------------------------
        # Position fully closed
        # -------------------------
        if new_qty == 0:
            realized = (price - existing.avg_price) * existing.quantity
            self.realized_pnl += realized
            del self.positions[symbol]
            return

        # -------------------------
        # Position flip (long → short or vice versa)
        # -------------------------
        if existing.quantity * new_qty < 0:
            realized = (price - existing.avg_price) * existing.quantity
            self.realized_pnl += realized
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=new_qty,
                avg_price=price,
                strategy_id=strategy_id,
            )
            return

        # -------------------------
        # Position increased (same direction)
        # -------------------------
        total_qty = existing.quantity + quantity
        weighted_price = (
            existing.avg_price * existing.quantity
            + price * quantity
        ) / total_qty

        self.positions[symbol] = replace(
            existing,
            quantity=total_qty,
            avg_price=weighted_price,
        )

    # ------------------------------------------------------------------
    # Portfolio-level computations (pure functions)
    # ------------------------------------------------------------------
    def total_notional(self, prices: Dict[Symbol, float]) -> float:
        return sum(
            pos.notional(prices[pos.symbol])
            for pos in self.positions.values()
            if pos.symbol in prices
        )

    def unrealized_pnl(self, prices: Dict[Symbol, float]) -> float:
        return sum(
            pos.unrealized_pnl(prices[pos.symbol])
            for pos in self.positions.values()
            if pos.symbol in prices
        )

    # ------------------------------------------------------------------
    # Snapshot creation
    # ------------------------------------------------------------------
    def snapshot(
        self,
        *,
        timestamp: datetime,
        prices: Optional[Dict[Symbol, float]] = None,
    ) -> PortfolioSnapshot:
        metrics: Dict[str, float] = {}

        if prices:
            metrics["total_notional"] = self.total_notional(prices)
            metrics["unrealized_pnl"] = self.unrealized_pnl(prices)
            metrics["equity"] = (
                self.cash
                + self.realized_pnl
                + metrics["unrealized_pnl"]
            )

        return PortfolioSnapshot(
            timestamp=timestamp,
            positions=dict(self.positions),  # shallow copy for immutability
            cash=self.cash,
            realized_pnl=self.realized_pnl,
            metrics=metrics,
        )
