from __future__ import annotations

from typing import Dict

from .types import AllocationInput, AllocationResult
from .constraints import (
    enforce_non_negative,
    enforce_total_capital,
    apply_max_per_strategy,
)


class AllocationEngine:
    """
    Pure allocation engine.

    Properties:
    - deterministic
    - side-effect free
    - restart-safe
    - idempotent
    """

    def __init__(
        self,
        *,
        max_per_strategy_fraction: float | None = None,
    ) -> None:
        if max_per_strategy_fraction is not None:
            if not (0.0 < max_per_strategy_fraction <= 1.0):
                raise ValueError("max_per_strategy_fraction must be in (0,1]")
        self._max_fraction = max_per_strategy_fraction

    def allocate(self, inp: AllocationInput) -> AllocationResult:
        weights = dict(inp.weights)
        enforce_non_negative(weights)

        if not weights or inp.capital <= 0:
            return AllocationResult(allocations={})

        total_weight = sum(weights.values())

        if total_weight <= 0:
            return AllocationResult(allocations={})

        # Normalize
        normalized: Dict[str, float] = {
            sid: w / total_weight for sid, w in weights.items()
        }

        allocations: Dict[str, float] = {
            sid: frac * inp.capital for sid, frac in normalized.items()
        }

        if self._max_fraction is not None:
            allocations = apply_max_per_strategy(
                allocations,
                self._max_fraction,
                inp.capital,
            )

        enforce_total_capital(allocations, inp.capital)

        return AllocationResult(allocations=dict(allocations))
