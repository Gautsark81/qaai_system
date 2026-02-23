# modules/strategies/registry.py

"""
Central registry for all production strategies.

RULES:
- Keys are stable strategy_type identifiers (used in StrategySpec)
- Values are concrete BaseStrategy subclasses
- No dynamic imports
- No fallbacks
- No defaults
"""

from typing import Dict, Type

from modules.strategies.base import BaseStrategy
from modules.strategies.ema_cross import EMACrossStrategy


STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "ema_cross": EMACrossStrategy,
}
