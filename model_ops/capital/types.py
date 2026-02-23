from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AllocationInput:
    weights: Dict[str, float]
    capital: float


@dataclass(frozen=True)
class AllocationResult:
    allocations: Dict[str, float]
    total_allocated: float

    @classmethod
    def empty(cls) -> "AllocationResult":
        return cls(allocations={}, total_allocated=0.0)
