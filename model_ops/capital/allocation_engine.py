from __future__ import annotations

from typing import Dict

from .types import AllocationInput, AllocationResult
from .constraints import CapitalConstraints


class AllocationEngine:
    """
    Pure capital allocation engine.

    Phase-11 invariants:
    - Deterministic
    - total_allocated <= capital
    - Explicit negative-weight rejection
    """

    def __init__(self, max_per_strategy_fraction: float | None = None):
        self._constraints = CapitalConstraints(
            max_per_strategy_fraction=max_per_strategy_fraction
        )

    def allocate(self, inp: AllocationInput) -> AllocationResult:
        if inp.capital <= 0.0 or not inp.weights:
            return AllocationResult.empty()

        # Explicit rejection (Phase-11 test)
        for sid, w in inp.weights.items():
            if w < 0.0:
                raise ValueError(f"Negative weight for strategy {sid}")

        sorted_items = sorted(inp.weights.items(), key=lambda kv: kv[0])

        weight_sum = sum(w for _, w in sorted_items)
        if weight_sum <= 0.0:
            return AllocationResult.empty()

        allocations: Dict[str, float] = {
            sid: inp.capital * (w / weight_sum)
            for sid, w in sorted_items
        }

        allocations = self._constraints.enforce_caps(
            allocations=allocations,
            total_capital=inp.capital,
        )

        total_allocated = sum(allocations.values())

        return AllocationResult(
            allocations=allocations,
            total_allocated=total_allocated,
        )
