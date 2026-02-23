# core/strategy_intelligence/verdict.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyIntelligenceVerdict:
    """
    Immutable, advisory-only diagnostic verdict for a strategy.
    """
    strategy_id: str
    health: str
    ssr: float
    promotion_signal: Optional[str]
