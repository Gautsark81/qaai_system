from datetime import datetime

from core.strategy_factory.capital.throttling import (
    evaluate_capital_throttle,
    get_throttle_audit_ledger,
)


def test_governance_chain_propagates_into_audit():

    ledger = get_throttle_audit_ledger()
    ledger._reset()

    chain_id = "GOV-TEST-001"

    evaluate_capital_throttle(
        governance_chain_id=chain_id,
        strategy_dna="DNA1",
        requested_capital=50000,
        last_allocation_at=None,
        cooldown_seconds=60,
        now=datetime.utcnow(),
    )

    events = ledger.events
    assert len(events) == 1
    assert events[0].governance_chain_id == chain_id