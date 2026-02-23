from dataclasses import dataclass
from typing import List, Optional

from core.capital.usage_ledger.models import CapitalUsageEntry
from core.capital.coordination.models import CoordinationDecision


@dataclass(frozen=True)
class RestartSnapshot:
    ledger_entries: List[CapitalUsageEntry]
    coordination_decision: Optional[CoordinationDecision]
    total_capital: Optional[float]
