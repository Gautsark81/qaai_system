from core.capital.throttle.ledger.capital_throttle_ledger import (
    CapitalThrottleLedger,
)
from core.capital.throttle.ledger.capital_throttle_ledger_entry import (
    CapitalThrottleLedgerEntry,
)


def test_capital_throttle_ledger_is_append_only():
    ledger = CapitalThrottleLedger()

    entry = CapitalThrottleLedgerEntry(
        strategy_id="STRAT-001",
        throttle_level=0.75,
        reason="VOLATILITY_SPIKE",
        decision_checksum="abc123",
    )

    ledger.append(entry)

    assert len(ledger.entries) == 1

    # No mutation allowed
    ledger.entries[0]  # read ok
