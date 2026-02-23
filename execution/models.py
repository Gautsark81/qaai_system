from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(slots=True)
class OrderIntent:
    """
    Broker-agnostic order intent.

    This is the only object the strategy/risk pipeline needs to produce.
    """
    strategy: str
    symbol: str
    side: str             # "BUY" / "SELL"
    quantity: float
    order_type: str = "MARKET"   # "MARKET" / "LIMIT"
    limit_price: Optional[float] = None
    meta: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionReport:
    """
    Minimal execution report for monitoring and state updates.
    """
    symbol: str
    side: str
    quantity: float
    status: str          # "ACCEPTED" / "REJECTED" / "FILLED" / etc.
    broker_order_id: Optional[str] = None
    message: str = ""
    meta: Dict[str, str] = field(default_factory=dict)
