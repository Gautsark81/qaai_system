# core/capital/capital_contracts.py

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StrategyCapitalSignal:
    """
    Capital-relevant signal for a strategy.

    This is a READ-ONLY contract used by:
    - capital allocators
    - evidence emitters
    - tests
    """
    ssr: float
    confidence: float
    regime_score: float


@dataclass(frozen=True)
class CapitalAllocationSuggestion:
    """
    Advisory capital allocation.
    """
    strategy_id: str
    suggested_weight: float     # 0.0 → 1.0
    max_allowed_weight: float
    risk_score: float
    rationale: str


@dataclass(frozen=True)
class CapitalOptimizationResult:
    """
    Full optimization output.
    """
    total_capital: float
    allocations: Dict[str, CapitalAllocationSuggestion]
    methodology: str
    notes: str
