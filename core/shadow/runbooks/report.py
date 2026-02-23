from dataclasses import dataclass
from typing import List, Dict, Any
from core.shadow.runbooks.models import RunbookEvent


@dataclass(frozen=True)
class RunbookReport:
    """
    Immutable runbook execution report.
    """
    executed: bool
    events: List[RunbookEvent]
    operator_acknowledged: bool
    evidence: Dict[str, Any]

    has_execution_authority: bool = False
    has_capital_authority: bool = False
