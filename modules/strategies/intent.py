# modules/strategies/intent.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal


@dataclass(frozen=True)
class StrategyIntent:
    strategy_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    confidence: float
    features_used: List[str]
    timestamp: datetime
