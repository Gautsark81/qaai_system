from decimal import Decimal
from datetime import datetime, timezone, date

from core.strategy_factory.capital.audit_event import build_capital_event_audit
from core.strategy_factory.capital.ledger_aggregation import build_capital_usage_ledger
from core.strategy_factory.capital.event_models import CapitalPolicySnapshot


class DummyEligibility:
    eligible = True
    reason = "Eligible"


class DummyAllocation:
    allocated_capital = 20000
    reason = "Initial allocation"


def test_allocation_audit_creates_ledger_entry():
    event = build_capital_event_audit(
        strategy_dna="dna_001",
        eligibility=DummyEligibility(),
        allocation=DummyAllocation(),
        memory_before=None,
        policy_snapshot=CapitalPolicySnapshot(
            requested_capital=20000,
            max_per_strategy=50000,
            global_cap_remaining=100000,
        ),
        created_at=datetime(2026, 1, 10, 9, 15, tzinfo=timezone.utc),
    )

    ledger = build_capital_usage_ledger([event])

    assert len(ledger) == 1

    entry = ledger[0]

    assert entry.source_event_id == event.fingerprint
    assert entry.source_event_type == "ALLOCATION"
    assert entry.scope == "STRATEGY"
    assert entry.scope_id == "dna_001"
    assert entry.capital_before == Decimal("0")
    assert entry.capital_after == Decimal("20000")
    assert entry.capital_delta == Decimal("20000")
    assert entry.reason == "Initial allocation"
