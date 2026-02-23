from dataclasses import dataclass
from typing import Dict
from core.capital.attribution.attribution_record import CapitalAttributionRecord


@dataclass(frozen=True)
class CapitalAllocationReport:
    """
    Immutable portfolio-level capital report.
    """
    total_strategies: int
    total_allocated: float
    allocations: Dict[str, CapitalAttributionRecord]
