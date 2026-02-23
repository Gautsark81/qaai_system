from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger
from core.capital.ledger.capital_scaling_ledger_entry import CapitalScalingLedgerEntry


def test_capital_scaling_ledger_contract():
    ledger = CapitalScalingLedger()

    assert hasattr(ledger, "append")
    assert hasattr(ledger, "entries")
    assert isinstance(ledger.entries, tuple)
