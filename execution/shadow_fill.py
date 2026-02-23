from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from data.execution.intent import ExecutionIntent


class PriceSource(Protocol):
    """
    Abstract market price source.
    Must be deterministic for the same (symbol, ts).
    """

    def price_at(self, symbol: str, ts: datetime) -> float:
        ...


@dataclass(frozen=True)
class ShadowFill:
    """
    Deterministic theoretical fill produced from a shadow intent.
    """
    intent_id: str
    symbol: str
    side: str
    quantity: int
    fill_price: float
    slippage_bps: float
    fill_ts: datetime


class ShadowFillEngine:
    """
    Converts ExecutionIntent -> ShadowFill using a deterministic price source.

    Invariants:
    - No randomness
    - No broker calls
    - Same input => same output
    """

    def __init__(
        self,
        *,
        price_source: PriceSource,
        slippage_bps: float = 0.0,
    ):
        self._prices = price_source
        self._slippage_bps = slippage_bps

    def fill(self, intent: ExecutionIntent) -> ShadowFill:
        """
        Produce a theoretical fill for a shadow execution intent.
        """

        base_price = self._prices.price_at(
            symbol=intent.symbol,
            ts=intent.signal_time,
        )

        if intent.side.upper() == "BUY":
            fill_price = base_price * (1 + self._slippage_bps / 10_000)
        elif intent.side.upper() == "SELL":
            fill_price = base_price * (1 - self._slippage_bps / 10_000)
        else:
            raise ValueError(f"invalid side: {intent.side}")

        return ShadowFill(
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            fill_price=round(fill_price, 4),
            slippage_bps=self._slippage_bps,
            fill_ts=intent.signal_time,
        )
