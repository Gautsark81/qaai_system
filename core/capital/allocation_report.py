from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StrategyAllocation:
    strategy_id: str
    allocated_capital: float


@dataclass(frozen=True)
class CapitalAllocationReport:
    """
    Immutable capital allocation snapshot.
    Governance-grade, read-only.
    """
    strategy_allocations: Dict[str, StrategyAllocation]


# ------------------------------------
# Canonical public aliases (INTENTIONAL)
# ------------------------------------

AllocationReport = CapitalAllocationReport
