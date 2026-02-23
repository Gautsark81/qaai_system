from datetime import datetime

from core.strategy_factory.capital.models import CapitalEligibilityDecision
from core.strategy_factory.capital.allocation_models import CapitalAllocationDecision
from core.strategy_factory.capital.audit_models import CapitalAllocationAudit
from core.strategy_factory.capital.fingerprints import (
    compute_capital_allocation_fingerprint,
)


def build_capital_allocation_audit(
    *,
    eligibility: CapitalEligibilityDecision,
    allocation: CapitalAllocationDecision,
    requested_capital: float,
    max_per_strategy: float,
    global_cap_remaining: float,
    created_at: datetime,
) -> CapitalAllocationAudit:
    """
    Build an immutable, deterministic audit record for capital allocation.

    Invariants:
    - Pure
    - No mutation
    - No implicit time
    - Governance-only
    """

    fingerprint = compute_capital_allocation_fingerprint(
        eligible=eligibility.eligible,
        eligibility_reason=eligibility.reason,
        requested_capital=requested_capital,
        max_per_strategy=max_per_strategy,
        global_cap_remaining=global_cap_remaining,
        approved_capital=allocation.approved_capital,
        allocation_reason=allocation.reason,
    )

    return CapitalAllocationAudit(
        created_at=created_at,

        eligible=eligibility.eligible,
        eligibility_reason=eligibility.reason,

        requested_capital=requested_capital,
        max_per_strategy=max_per_strategy,
        global_cap_remaining=global_cap_remaining,

        approved_capital=allocation.approved_capital,
        allocation_reason=allocation.reason,

        decision_fingerprint=fingerprint,
    )
