from typing import Dict

from core.capital.allocation_report import (
    AllocationReport,
    StrategyAllocation,
)

from .models import ConcentrationWarning

# ----------------------------------------
# Explicit re-export for test visibility
# ----------------------------------------
__all__ = [
    "AllocationReport",
    "StrategyAllocation",
    "build_concentration_warnings",
]


def build_concentration_warnings(
    report: AllocationReport,
    threshold: float = 0.7,
) -> Dict[str, ConcentrationWarning]:
    """
    Advisory-only concentration governance.

    Guarantees:
    - No execution authority
    - No mutation
    - Deterministic
    """

    allocations = report.strategy_allocations

    total_allocated = (
        sum(
            map(
                lambda a: a.allocated_capital,
                allocations.values(),
            )
        )
        or 1.0
    )

    return dict(
        map(
            lambda item: (
                item[0],
                ConcentrationWarning(
                    strategy_id=item[0],
                    allocated_capital=item[1].allocated_capital,
                    portfolio_fraction=(
                        item[1].allocated_capital / total_allocated
                    ),
                    threshold=threshold,
                ),
            ),
            filter(
                lambda item: (
                    item[1].allocated_capital / total_allocated
                )
                >= threshold,
                allocations.items(),
            ),
        )
    )
