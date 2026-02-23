from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CapitalAllocationResult:
    strategy_id: str
    allocated_capital: float
    rationale: List[str]
