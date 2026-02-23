from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class AllocationInput:
    strategy_id: str
    ssr: float
    stability_stddev: float
    regime_match: bool


@dataclass(frozen=True)
class AllocationResult:
    strategy_id: str
    weight: float


class PaperCapitalAllocator:
    """
    Shadow capital allocator.

    Produces proportional capital weights only.
    """

    def __init__(self, *, min_ssr: float = 0.8):
        self._min_ssr = min_ssr

    def allocate(
        self,
        inputs: Iterable[AllocationInput],
    ) -> List[AllocationResult]:
        # Filter eligible strategies
        eligible: List[AllocationInput] = [
            i
            for i in inputs
            if i.ssr >= self._min_ssr and i.regime_match
        ]

        if not eligible:
            return []

        raw_weights: Dict[str, float] = {}
        for i in eligible:
            raw = i.ssr / (1.0 + max(0.0, i.stability_stddev))
            raw_weights[i.strategy_id] = raw

        total = sum(raw_weights.values())
        if total <= 0:
            return []

        return [
            AllocationResult(
                strategy_id=sid,
                weight=raw / total,
            )
            for sid, raw in raw_weights.items()
        ]
