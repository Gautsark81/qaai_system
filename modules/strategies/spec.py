# modules/strategies/spec.py

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    strategy_type: str
    version: str
    symbol: str
    timeframe: str
    params: Mapping[str, object]
