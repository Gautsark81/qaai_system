from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AllocationInput:
    """
    Immutable allocation request.

    weights:
        strategy_id -> desired raw weight (not yet normalized)

    capital:
        total available capital (0.0–1.0 normalized or absolute)
    """
    weights: Dict[str, float]
    capital: float


@dataclass(frozen=True)
class AllocationResult:
    """
    Final allocation result.

    allocations:
        strategy_id -> allocated capital (same unit as input capital)
    """
    allocations: Dict[str, float]

    @property
    def total_allocated(self) -> float:
        return sum(self.allocations.values())
