from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from execution.shadow_fill import ShadowFill


class ExitPriceSource(Protocol):
    """
    Deterministic exit price provider.
    Example: mark-to-market, fixed horizon close, next bar VWAP.
    """

    def exit_price_at(
        self,
        symbol: str,
        entry_ts: datetime,
    ) -> float:
        ...


@dataclass(frozen=True)
class ShadowPnL:
    """
    Immutable PnL outcome for a shadow execution.
    """
    intent_id: str
    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float
    gross_pnl: float
    fees: float
    net_pnl: float
    holding_period_sec: int


class ShadowPnLEngine:
    """
    Computes deterministic PnL for a ShadowFill.

    Invariants:
    - No randomness
    - No broker calls
    - Same input => same output
    """

    def __init__(
        self,
        *,
        exit_price_source: ExitPriceSource,
        fee_bps: float = 0.0,
    ):
        self._exit_prices = exit_price_source
        self._fee_bps = fee_bps

    def compute(
        self,
        fill: ShadowFill,
        *,
        exit_ts: datetime,
    ) -> ShadowPnL:
        exit_price = self._exit_prices.exit_price_at(
            symbol=fill.symbol,
            entry_ts=fill.fill_ts,
        )

        if fill.side.upper() == "BUY":
            gross = (exit_price - fill.fill_price) * fill.quantity
        elif fill.side.upper() == "SELL":
            gross = (fill.fill_price - exit_price) * fill.quantity
        else:
            raise ValueError(f"invalid side: {fill.side}")

        notional = fill.fill_price * fill.quantity
        fees = notional * (self._fee_bps / 10_000)

        net = gross - fees

        holding_sec = int((exit_ts - fill.fill_ts).total_seconds())

        return ShadowPnL(
            intent_id=fill.intent_id,
            symbol=fill.symbol,
            side=fill.side,
            quantity=fill.quantity,
            entry_price=fill.fill_price,
            exit_price=exit_price,
            gross_pnl=round(gross, 4),
            fees=round(fees, 4),
            net_pnl=round(net, 4),
            holding_period_sec=holding_sec,
        )
