from datetime import datetime

from core.strategy_factory.capital.models import CapitalEligibilityDecision
from core.strategy_factory.capital.allocation_models import CapitalAllocationDecision
from core.strategy_factory.capital.audit import build_capital_allocation_audit


def test_capital_allocation_audit_is_deterministic():
    ts = datetime(2025, 1, 1)

    eligibility = CapitalEligibilityDecision(
        eligible=True,
        reason="eligible",
    )

    allocation = CapitalAllocationDecision(
        approved_capital=50_000,
        reason="capped by policy",
    )

    audit1 = build_capital_allocation_audit(
        eligibility=eligibility,
        allocation=allocation,
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
        created_at=ts,
    )

    audit2 = build_capital_allocation_audit(
        eligibility=eligibility,
        allocation=allocation,
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
        created_at=ts,
    )

    assert audit1 == audit2


def test_capital_allocation_audit_fingerprint_present():
    ts = datetime(2025, 1, 1)

    audit = build_capital_allocation_audit(
        eligibility=CapitalEligibilityDecision(
            eligible=False,
            reason="not eligible",
        ),
        allocation=CapitalAllocationDecision(
            approved_capital=0,
            reason="denied",
        ),
        requested_capital=100_000,
        max_per_strategy=50_000,
        global_cap_remaining=1_000_000,
        created_at=ts,
    )

    assert audit.decision_fingerprint
