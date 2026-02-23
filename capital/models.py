from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CapitalAllocation:
    strategy_id: str
    strategy_version: str
    stage: str  # PAPER | LIVE

    allocated_capital: float
    weight: float

    status: str  # ACTIVE | THROTTLED | FROZEN
    reason: str | None


@dataclass(frozen=True)
class CapitalAllocationPlan:
    allocation_id: UUID
    created_at: datetime
    total_allocatable_capital: float
    allocations: list[CapitalAllocation]
