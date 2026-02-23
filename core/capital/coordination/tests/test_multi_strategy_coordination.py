from datetime import datetime

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.coordination.coordinator import CapitalCoordinator
from core.capital.coordination.models import (
    CapitalRequest,
    CoordinationDecision,
)


def test_single_strategy_within_limits():
    ledger = CapitalUsageLedger()
    coordinator = CapitalCoordinator(total_capital=100_000)

    req = CapitalRequest(
        strategy_id="A",
        requested_amount=40_000,
        timestamp=datetime.utcnow(),
    )

    decision = coordinator.coordinate([req], ledger)

    assert decision.granted["A"] == 40_000
    assert decision.remaining_capital == 60_000


def test_two_strategies_no_conflict():
    ledger = CapitalUsageLedger()
    coordinator = CapitalCoordinator(total_capital=100_000)

    requests = [
        CapitalRequest("A", 30_000, datetime.utcnow()),
        CapitalRequest("B", 20_000, datetime.utcnow()),
    ]

    decision = coordinator.coordinate(requests, ledger)

    assert decision.granted["A"] == 30_000
    assert decision.granted["B"] == 20_000
    assert decision.remaining_capital == 50_000


def test_conflict_resolves_deterministically():
    ledger = CapitalUsageLedger()
    coordinator = CapitalCoordinator(total_capital=50_000)

    requests = [
        CapitalRequest("A", 40_000, datetime.utcnow()),
        CapitalRequest("B", 40_000, datetime.utcnow()),
    ]

    decision = coordinator.coordinate(requests, ledger)

    # Deterministic tie-break: strategy_id lexical order
    assert decision.granted["A"] == 40_000
    assert decision.granted["B"] == 10_000
    assert decision.remaining_capital == 0


def test_existing_engaged_capital_respected():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 60_000, datetime.utcnow(), "existing")

    coordinator = CapitalCoordinator(total_capital=100_000)

    requests = [
        CapitalRequest("B", 50_000, datetime.utcnow()),
    ]

    decision = coordinator.coordinate(requests, ledger)

    assert decision.granted["B"] == 40_000
    assert decision.remaining_capital == 0


def test_decision_contains_explanation():
    ledger = CapitalUsageLedger()
    coordinator = CapitalCoordinator(total_capital=100_000)

    req = CapitalRequest("A", 80_000, datetime.utcnow())

    decision = coordinator.coordinate([req], ledger)

    explanation = decision.explanations["A"]
    assert "requested" in explanation
    assert "granted" in explanation
    assert "available" in explanation
