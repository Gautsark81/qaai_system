from dataclasses import dataclass
from datetime import timedelta
from typing import List, Set


@dataclass(frozen=True)
class MarketInteractionFingerprint:
    instruments: List[str]
    avg_holding_period: timedelta
    trade_frequency_per_day: float
    market_regimes: Set[str]
    session_bias: Set[str]
