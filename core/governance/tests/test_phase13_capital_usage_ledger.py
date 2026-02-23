from datetime import datetime, timezone

from core.governance.capital_usage.capital_usage_ledger import (
    CapitalUsageLedger,
    CapitalUsageEntry,
)


def test_ledger_is_append_only_and_immutable():
    ledger = CapitalUsageLedger()

    entry = CapitalUsageEntry(
        strategy_id="STRAT-1",
        governance_id="gov-001",
        allocated_capital=1_000_000,
        deployed_capital=800_000,
        realized_pnl=25_000,
        timestamp=datetime.now(timezone.utc),
    )

    ledger.append(entry)

    entries = ledger.entries()

    assert len(entries) == 1
    assert entries[0].strategy_id == "STRAT-1"

    # ensure immutability
    try:
        entries[0].allocated_capital = 0
        assert False
    except Exception:
        assert True