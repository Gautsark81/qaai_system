import pytest
from dataclasses import FrozenInstanceError

from core.capital.ledger.capital_scaling_ledger_entry import (
    CapitalScalingLedgerEntry,
)


def test_governance_id_is_immutable():
    entry = CapitalScalingLedgerEntry(
        strategy_id="STRAT-IMMUTABLE",
        previous_capital=1_000_000,
        new_capital=900_000,
        scale_factor=0.9,
        governance_id="gov-lock",
    )

    with pytest.raises(FrozenInstanceError):
        entry.governance_id = "tampered"
