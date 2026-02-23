import pytest
from datetime import datetime, timezone
from core.capital.ledger.capital_scaling_ledger_entry import CapitalScalingLedgerEntry


def test_capital_scaling_ledger_entry_is_immutable():
    entry = CapitalScalingLedgerEntry(
        strategy_id="STRAT-1",
        previous_capital=1_000_000,
        new_capital=1_200_000,
        scale_factor=1.2,
        decision_reason="CAPITAL_SCALE_UP",
        decision_checksum="abc123",
        timestamp=datetime.now(timezone.utc),
    )

    with pytest.raises(Exception):
        entry.new_capital = 0
