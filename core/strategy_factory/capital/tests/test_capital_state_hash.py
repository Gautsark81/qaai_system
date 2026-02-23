from datetime import datetime, timezone

from core.strategy_factory.capital.ledger_models import (
    CapitalLedgerEntry,
    CapitalLedgerEventType,
)
from core.strategy_factory.capital.state_hash import (
    compute_capital_ledger_state_hash,
)


def test_hash_deterministic_order_independent():
    e1 = CapitalLedgerEntry(
        strategy_dna="A",
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=10.0,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    e2 = CapitalLedgerEntry(
        strategy_dna="B",
        event_type=CapitalLedgerEventType.CAPITAL_RELEASED,
        amount=5.0,
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )

    h1 = compute_capital_ledger_state_hash([e1, e2])
    h2 = compute_capital_ledger_state_hash([e2, e1])

    assert h1 == h2


def test_hash_changes_on_mutation():
    e1 = CapitalLedgerEntry(
        strategy_dna="A",
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=10.0,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    e2 = CapitalLedgerEntry(
        strategy_dna="A",
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=11.0,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    h1 = compute_capital_ledger_state_hash([e1])
    h2 = compute_capital_ledger_state_hash([e2])

    assert h1 != h2


def test_float_stability():
    e1 = CapitalLedgerEntry(
        strategy_dna="A",
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=10.0000000001,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    e2 = CapitalLedgerEntry(
        strategy_dna="A",
        event_type=CapitalLedgerEventType.ALLOCATION_APPROVED,
        amount=10.0000000001000001,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    h1 = compute_capital_ledger_state_hash([e1])
    h2 = compute_capital_ledger_state_hash([e2])

    assert h1 == h2