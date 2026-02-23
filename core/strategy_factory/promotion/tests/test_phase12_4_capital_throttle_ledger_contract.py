from core.capital.throttle.ledger.capital_throttle_ledger import (
    CapitalThrottleLedger,
)


def test_capital_throttle_ledger_contract():
    ledger = CapitalThrottleLedger()

    assert hasattr(ledger, "append")
    assert hasattr(ledger, "entries")
    assert isinstance(ledger.entries, tuple)
