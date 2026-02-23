from __future__ import annotations

from typing import Dict


class CapitalConstraintError(RuntimeError):
    """
    Raised when a hard capital safety invariant is violated.

    Phase-11 contract:
    - Explicit error type for capital constraint violations
    - Never silently swallowed
    """


class CapitalConstraints:
    """
    Hard capital safety constraints.

    Phase-11 invariants:
    - Total allocation must never exceed total capital
    - Optional per-strategy cap (fraction of total capital)
    """

    def __init__(self, max_per_strategy_fraction: float | None = None):
        if max_per_strategy_fraction is not None:
            if not (0.0 < max_per_strategy_fraction <= 1.0):
                raise CapitalConstraintError(
                    "max_per_strategy_fraction must be in (0, 1]"
                )
        self._max_per_strategy_fraction = max_per_strategy_fraction

    def enforce_caps(
        self,
        allocations: Dict[str, float],
        total_capital: float,
    ) -> Dict[str, float]:
        """
        Enforce per-strategy and total-capital constraints.

        Deterministic, side-effect free.
        """

        capped = dict(allocations)

        # Per-strategy cap
        if self._max_per_strategy_fraction is not None:
            max_allowed = total_capital * self._max_per_strategy_fraction
            for sid, alloc in capped.items():
                capped[sid] = min(alloc, max_allowed)

        total = sum(capped.values())

        if total <= total_capital:
            return capped

        if total_capital <= 0.0:
            raise CapitalConstraintError(
                "Total capital must be positive"
            )

        # Proportional rescale (hard safety)
        scale = total_capital / total
        return {sid: alloc * scale for sid, alloc in capped.items()}
