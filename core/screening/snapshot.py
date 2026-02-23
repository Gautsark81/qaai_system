# core/screening/snapshot.py

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class MarketSnapshot:
    """
    Immutable point-in-time market state used for screening.
    Matches test expectations exactly.
    """
    symbol: str
    timeframe: int
    close: float
    volume: float
    atr: float
    volatility: float
    features: Optional[Any] = None
