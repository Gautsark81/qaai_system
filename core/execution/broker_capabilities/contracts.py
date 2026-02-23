# core/execution/broker_capabilities/contracts.py

from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class BrokerCapabilities:
    """
    Immutable, declarative broker capability contract.

    Descriptive only.
    No execution authority.
    """

    broker_name: str
    version: str

    supports_market_orders: bool
    supports_limit_orders: bool
    supports_intraday: bool
    supports_bracket_orders: bool
    supports_partial_fills: bool
    supports_live_position_query: bool
    supports_cancel_replace: bool
    supports_replay: bool

    def supported_operations(self) -> FrozenSet[str]:
        ops = set()
        if self.supports_market_orders:
            ops.add("MARKET_ORDER")
        if self.supports_limit_orders:
            ops.add("LIMIT_ORDER")
        if self.supports_intraday:
            ops.add("INTRADAY")
        if self.supports_bracket_orders:
            ops.add("BRACKET_ORDER")
        if self.supports_partial_fills:
            ops.add("PARTIAL_FILL")
        if self.supports_live_position_query:
            ops.add("POSITION_QUERY")
        if self.supports_cancel_replace:
            ops.add("CANCEL_REPLACE")
        if self.supports_replay:
            ops.add("REPLAY")

        return frozenset(ops)
