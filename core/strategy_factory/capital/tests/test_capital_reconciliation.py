from datetime import datetime, timezone, date
from decimal import Decimal

from core.strategy_factory.capital.ledger_models import CapitalUsageLedgerEntry
from core.strategy_factory.capital.ledger_reconciliation import reconcile_capital_usage_ledger


def test_reconciliation_happy_path():
    entries = [
        CapitalUsageLedgerEntry(
            ledger_id="l1",
            timestamp_utc=datetime(2026, 1, 10, 9, 15, tzinfo=timezone.utc),
            trading_day=date(2026, 1, 10),
            source_event_id="e1",
            source_event_type="ALLOCATION",
            scope="STRATEGY",
            scope_id="dna_001",
            capital_before=Decimal("0"),
            capital_after=Decimal("20000"),
            capital_delta=Decimal("20000"),
            reason="Initial allocation",
        ),
        CapitalUsageLedgerEntry(
            ledger_id="l2",
            timestamp_utc=datetime(2026, 1, 10, 9, 30, tzinfo=timezone.utc),
            trading_day=date(2026, 1, 10),
            source_event_id="e2",
            source_event_type="ALLOCATION",
            scope="STRATEGY",
            scope_id="dna_001",
            capital_before=Decimal("20000"),
            capital_after=Decimal("30000"),
            capital_delta=Decimal("10000"),
            reason="Top-up",
        ),
    ]

    report = reconcile_capital_usage_ledger(entries)

    assert report.is_consistent is True
    assert report.violations == []
    assert report.entry_count == 2
