from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class GovernanceFingerprint:
    allowed_environments: Set[str]
    requires_human_approval: bool
    max_capital_allocation_pct: float
    kill_switch_required: bool
    audit_level: str
