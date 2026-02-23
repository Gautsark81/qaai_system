from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EnsembleStrategy:
    strategy_id: str
    ssr: float
    drawdown_pct: float = 0.0


@dataclass(frozen=True)
class AllocationResult:
    allocations: Dict[str, float]
    tier_weights: Dict[str, int]
    drawdown_multipliers: Dict[str, float]
    suspensions: Dict[str, str]
    governance_adjustments: Dict[str, float]
    snapshot_hash: str