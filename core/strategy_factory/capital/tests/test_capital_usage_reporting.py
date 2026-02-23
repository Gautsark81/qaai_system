from __future__ import annotations

from datetime import datetime, date, timezone
from decimal import Decimal

from core.strategy_factory.capital.ledger_models import CapitalUsageLedgerEntry
from core.strategy_factory.capital.reporting import (
    build_capital_usage_report,
)


def test_capital_usage_report_basic_summary():
    """
    C4.7 — Capital usage reporting provides
    deterministic, audit-safe summary statistics.
    """

    ts = datetime(2026, 1, 10, 9, 15, tzinfo=timezone.utc)

    entries = [
        CapitalUsageLedgerEntry(
            ledger_id="l1",
            timestamp_utc=ts,
            trading_day=date(2026, 1, 10),
            source_event_id="e1",
            source_event_type="ALLOCATION",
            scope="STRATEGY",
            scope_id="s1",
            capital_before=Decimal("0"),
            capital_after=Decimal("100"),
            capital_delta=Decimal("100"),
            reason="alloc",
        ),
        CapitalUsageLedgerEntry(
            ledger_id="l2",
            timestamp_utc=ts,
            trading_day=date(2026, 1, 10),
            source_event_id="e2",
            source_event_type="ALLOCATION",
            scope="STRATEGY",
            scope_id="s1",
            capital_before=Decimal("100"),
            capital_after=Decimal("60"),
            capital_delta=Decimal("-40"),
            reason="release",
        ),
        CapitalUsageLedgerEntry(
            ledger_id="l3",
            timestamp_utc=ts,
            trading_day=date(2026, 1, 10),
            source_event_id="e3",
            source_event_type="ALLOCATION",
            scope="STRATEGY",
            scope_id="s2",
            capital_before=Decimal("0"),
            capital_after=Decimal("50"),
            capital_delta=Decimal("50"),
            reason="alloc",
        ),
    ]

    report = build_capital_usage_report(entries)

    assert report.entry_count == 3
    assert report.total_allocated == 150.0
    assert report.total_released == 40.0
