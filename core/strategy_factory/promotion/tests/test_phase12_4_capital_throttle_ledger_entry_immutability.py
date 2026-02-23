import pytest

from core.capital.throttle.ledger.capital_throttle_ledger_entry import (
    CapitalThrottleLedgerEntry,
)


def test_capital_throttle_ledger_entry_is_immutable():
    entry = CapitalThrottleLedgerEntry(
        strategy_id="STRAT-IMMUTABLE",
        throttle_level=0.5,
        reason="DRAWDOWN",
        decision_checksum="hash123",
    )

    with pytest.raises(Exception):
        entry.throttle_level = 1.0
