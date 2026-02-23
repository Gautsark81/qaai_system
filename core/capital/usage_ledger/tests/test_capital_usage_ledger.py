import pytest
from datetime import datetime, timedelta

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.usage_ledger.models import (
    CapitalEventType,
    CapitalUsageEntry,
)


def test_ledger_starts_empty():
    ledger = CapitalUsageLedger()
    assert ledger.entries() == []
    assert ledger.total_used_capital() == 0


def test_records_capital_allocation():
    ledger = CapitalUsageLedger()
    ts = datetime.utcnow()

    ledger.record_allocation(
        strategy_id="strat_A",
        amount=100000,
        timestamp=ts,
        reason="initial allocation",
    )

    assert len(ledger.entries()) == 1
    assert ledger.total_used_capital() == 100000


def test_records_capital_consumption():
    ledger = CapitalUsageLedger()

    ledger.record_allocation(
        strategy_id="strat_A",
        amount=100000,
        timestamp=datetime.utcnow(),
        reason="allocation",
    )

    ledger.record_consumption(
        strategy_id="strat_A",
        amount=40000,
        timestamp=datetime.utcnow(),
        reason="position opened",
    )

    assert ledger.total_used_capital() == 40000


def test_records_capital_release():
    ledger = CapitalUsageLedger()

    ledger.record_allocation("strat_A", 100000, datetime.utcnow(), "alloc")
    ledger.record_consumption("strat_A", 60000, datetime.utcnow(), "open")
    ledger.record_release("strat_A", 60000, datetime.utcnow(), "close")

    assert ledger.total_used_capital() == 0


def test_strategy_level_attribution():
    ledger = CapitalUsageLedger()

    ledger.record_allocation("A", 100000, datetime.utcnow(), "alloc")
    ledger.record_allocation("B", 50000, datetime.utcnow(), "alloc")

    ledger.record_consumption("A", 40000, datetime.utcnow(), "trade")
    ledger.record_consumption("B", 10000, datetime.utcnow(), "trade")

    assert ledger.used_capital_by_strategy("A") == 40000
    assert ledger.used_capital_by_strategy("B") == 10000


def test_ledger_is_append_only():
    ledger = CapitalUsageLedger()

    ledger.record_allocation("A", 100000, datetime.utcnow(), "alloc")

    with pytest.raises(AttributeError):
        ledger._entries.clear()


def test_replay_reconstructs_state():
    ledger = CapitalUsageLedger()
    ts = datetime.utcnow()

    ledger.record_allocation("A", 100000, ts, "alloc")
    ledger.record_consumption("A", 30000, ts + timedelta(seconds=1), "trade")
    ledger.record_release("A", 30000, ts + timedelta(seconds=2), "close")

    snapshot = ledger.entries()

    replayed = CapitalUsageLedger.replay(snapshot)

    assert replayed.total_used_capital() == 0
    assert replayed.used_capital_by_strategy("A") == 0


def test_entries_are_immutable():
    ledger = CapitalUsageLedger()

    ledger.record_allocation("A", 100000, datetime.utcnow(), "alloc")
    entry = ledger.entries()[0]

    with pytest.raises(AttributeError):
        entry.amount = 999999
