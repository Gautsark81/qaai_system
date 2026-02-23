"""
modules/strategies/strategy_context.py

Canonical, immutable input contract for ALL strategies.

This file defines the ONLY allowed input surface
between data/feature layers and strategy logic.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class StrategyContext:
    """
    Immutable snapshot of all information a strategy may consume.

    Rules:
    - Strategies may ONLY read from this object
    - No IO
    - No data fetching
    - No mutation
    """

    symbol: str
    timeframe: str
    features: Dict[str, Any]
    metadata: Dict[str, Any]

    def get(self, key: str, default=None):
        return self.features.get(key, default)
