from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.strategy_factory.capital.allocation_models import (
    CapitalAllocationDecision,
)


@dataclass(frozen=True)
class CapitalAllocationMemory:
    """
    Immutable memory of capital allocation governance decisions.

    NOTE:
    - Tracks decisions, not execution
    - Zero allocation is still a governance event
    - Deterministic and audit-safe
    """

    last_allocated_capital: float
    last_allocation_at: datetime
    allocation_count: int
    cumulative_allocated: float
    rejection_count: int


def update_capital_allocation_memory(
    *,
    previous: Optional[CapitalAllocationMemory],
    allocation: CapitalAllocationDecision,
    created_at: datetime,
) -> CapitalAllocationMemory:
    """
    Update capital allocation memory based on a new allocation decision.

    Governance-only:
    - No execution
    - No broker state
    - No balances
    - No mutation

    Deterministic:
    same inputs -> same output
    """

    allocated = allocation.allocated_capital
    is_rejection = allocated <= 0.0

    if previous is None:
        return CapitalAllocationMemory(
            last_allocated_capital=allocated,
            last_allocation_at=created_at,
            allocation_count=1,
            cumulative_allocated=max(allocated, 0.0),
            rejection_count=1 if is_rejection else 0,
        )

    return CapitalAllocationMemory(
        last_allocated_capital=allocated,
        last_allocation_at=created_at,
        allocation_count=previous.allocation_count + 1,
        cumulative_allocated=(
            previous.cumulative_allocated + max(allocated, 0.0)
        ),
        rejection_count=(
            previous.rejection_count + (1 if is_rejection else 0)
        ),
    )
