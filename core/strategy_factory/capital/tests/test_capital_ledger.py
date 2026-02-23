from datetime import datetime

from core.strategy_factory.capital.capital_ledger import (
    CapitalUsageLedger,
)


def test_event_is_recorded():
    ledger = CapitalUsageLedger()

    now = datetime(2026, 1, 1)

    ledger.record(
        strategy_dna="STRAT_A",
        requested_capital=1000,
        approved_capital=800,
        deployed_capital=800,
        now=now,
    )

    assert len(ledger.events) == 1


def test_append_only_behavior():
    ledger = CapitalUsageLedger()

    now = datetime(2026, 1, 1)

    ledger.record(
        strategy_dna="A",
        requested_capital=100,
        approved_capital=100,
        deployed_capital=100,
        now=now,
    )

    ledger.record(
        strategy_dna="B",
        requested_capital=200,
        approved_capital=200,
        deployed_capital=150,
        now=now,
    )

    assert len(ledger.events) == 2


def test_totals_computation():
    ledger = CapitalUsageLedger()

    now = datetime(2026, 1, 1)

    ledger.record(
        strategy_dna="A",
        requested_capital=100,
        approved_capital=100,
        deployed_capital=80,
        now=now,
    )

    ledger.record(
        strategy_dna="B",
        requested_capital=200,
        approved_capital=150,
        deployed_capital=150,
        now=now,
    )

    assert ledger.total_requested() == 300
    assert ledger.total_approved() == 250
    assert ledger.total_deployed() == 230


def test_utilization_ratio():
    ledger = CapitalUsageLedger()

    now = datetime(2026, 1, 1)

    ledger.record(
        strategy_dna="A",
        requested_capital=100,
        approved_capital=100,
        deployed_capital=50,
        now=now,
    )

    assert ledger.utilization_ratio() == 0.5


def test_zero_approved_safe():
    ledger = CapitalUsageLedger()

    assert ledger.utilization_ratio() == 0.0