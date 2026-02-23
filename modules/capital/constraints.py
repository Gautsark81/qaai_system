from __future__ import annotations

from typing import Dict


class AllocationConstraintError(ValueError):
    pass


def enforce_non_negative(weights: Dict[str, float]) -> Dict[str, float]:
    for k, v in weights.items():
        if v < 0:
            raise AllocationConstraintError(
                f"Negative allocation weight not allowed: {k}={v}"
            )
    return weights


def enforce_total_capital(
    allocations: Dict[str, float],
    total_capital: float,
) -> Dict[str, float]:
    allocated = sum(allocations.values())
    if allocated > total_capital + 1e-9:
        raise AllocationConstraintError(
            f"Allocated capital {allocated} exceeds total {total_capital}"
        )
    return allocations


def apply_max_per_strategy(
    allocations: Dict[str, float],
    max_fraction: float,
    total_capital: float,
) -> Dict[str, float]:
    """
    Cap any single strategy allocation to max_fraction of total capital.
    """
    capped: Dict[str, float] = {}
    max_cap = total_capital * max_fraction

    for sid, value in allocations.items():
        capped[sid] = min(value, max_cap)

    return capped
