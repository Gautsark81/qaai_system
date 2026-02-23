from core.capital.throttle.ledger.capital_throttle_ledger import (
    CapitalThrottleLedger,
)
from core.capital.throttle.ledger.capital_throttle_ledger_entry import (
    CapitalThrottleLedgerEntry,
)


def test_capital_throttle_ledger_is_deterministic():
    ledger = CapitalThrottleLedger()

    entry = CapitalThrottleLedgerEntry(
        strategy_id="STRAT-DET",
        throttle_level=0.9,
        reason="CAP_EXPOSURE",
        decision_checksum="det123",
    )

    ledger.append(entry)
    ledger.append(entry)

    assert ledger.entries[0] == ledger.entries[1]
