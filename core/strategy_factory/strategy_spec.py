# core/strategy_factory/strategy_spec.py

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class StrategySpec:
    """
    Canonical definition of a generated strategy.
    """
    strategy_id: str
    archetype: str
    timeframe: str
    indicators: Dict[str, float]
    risk_model: Dict[str, float]
    constraints: Dict[str, float]
    tags: List[str]
