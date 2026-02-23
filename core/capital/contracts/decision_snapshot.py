from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class CapitalDecisionSnapshot:
    """
    Immutable per-strategy capital decision artifact.
    """

    strategy_id: str
    final_allocation: float
    raw_fitness: float
    fragility_penalty: float
    regime: object
    reasons: List[str]
    diagnostics: Dict[str, Any]
