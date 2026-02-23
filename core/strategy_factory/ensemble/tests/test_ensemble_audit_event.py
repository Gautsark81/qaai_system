from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
    EnsembleAllocationAuditEvent,
)


def test_audit_event_reproducibility():
    strategies = [EnsembleStrategy("A", 90)]
    snap = EnsembleSnapshot(strategies, 1000, 1000, 1000, 1000)

    result = EnsembleAllocator.allocate(snap)
    event = EnsembleAllocationAuditEvent.from_result(result)

    json1 = event.to_json()
    json2 = event.to_json()

    assert json1 == json2