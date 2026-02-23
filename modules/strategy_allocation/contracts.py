from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AllocationCandidate:
    strategy_id: str
    symbol: str
    health_score: float          # from C2.1
    fitness_score: float         # from C1
    max_drawdown: float          # realized DD (0–1)
    age_steps: int               # longevity
    state: str                   # ACTIVE / WARNING


@dataclass(frozen=True)
class AllocationResult:
    weights: Dict[str, float]    # strategy_id -> weight
    reasons: Dict[str, List[str]]
