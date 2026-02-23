from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CapitalAllocationAudit:
    """
    Immutable audit record for a capital allocation decision.

    Governance-only artifact:
    - Deterministic
    - Fingerprinted
    - No behavior
    """

    created_at: datetime

    # Eligibility
    eligible: bool
    eligibility_reason: str

    # Allocation inputs
    requested_capital: float
    max_per_strategy: float
    global_cap_remaining: float

    # Allocation outcome
    approved_capital: float
    allocation_reason: str

    # Deterministic fingerprint
    decision_fingerprint: str
