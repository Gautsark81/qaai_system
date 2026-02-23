from datetime import datetime

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.coordination.coordinator import CapitalCoordinator
from core.capital.coordination.models import CapitalRequest
from core.runtime.restart.reconstructor import SystemReconstructor


def test_restart_rebuilds_same_used_capital():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 100_000, datetime.utcnow(), "alloc")
    ledger.record_consumption("A", 40_000, datetime.utcnow(), "trade")

    snapshot = SystemReconstructor.capture_snapshot(ledger)

    rebuilt = SystemReconstructor.rebuild(snapshot)

    assert rebuilt.ledger.total_used_capital() == 40_000
    assert rebuilt.ledger.used_capital_by_strategy("A") == 40_000


def test_restart_is_idempotent():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 50_000, datetime.utcnow(), "alloc")

    snapshot = SystemReconstructor.capture_snapshot(ledger)

    r1 = SystemReconstructor.rebuild(snapshot)
    r2 = SystemReconstructor.rebuild(snapshot)

    assert r1.ledger.total_used_capital() == r2.ledger.total_used_capital()


def test_restart_preserves_coordination_outcome():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 60_000, datetime.utcnow(), "alloc")

    coordinator = CapitalCoordinator(total_capital=100_000)

    reqs = [CapitalRequest("B", 50_000, datetime.utcnow())]
    decision_before = coordinator.coordinate(reqs, ledger)

    snapshot = SystemReconstructor.capture_snapshot(
        ledger=ledger,
        coordination_decision=decision_before,
        total_capital=100_000,
    )

    rebuilt = SystemReconstructor.rebuild(snapshot)

    decision_after = rebuilt.coordinator.coordinate(reqs, rebuilt.ledger)

    assert decision_after.granted == decision_before.granted
    assert decision_after.remaining_capital == decision_before.remaining_capital


def test_restart_does_not_duplicate_entries():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 100_000, datetime.utcnow(), "alloc")

    snapshot = SystemReconstructor.capture_snapshot(ledger)

    rebuilt = SystemReconstructor.rebuild(snapshot)

    assert len(rebuilt.ledger.entries()) == 1
