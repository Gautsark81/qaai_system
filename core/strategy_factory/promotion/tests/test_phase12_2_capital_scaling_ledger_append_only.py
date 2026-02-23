import pytest
from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger


def test_capital_scaling_ledger_is_append_only():
    ledger = CapitalScalingLedger()

    with pytest.raises(AttributeError):
        ledger.entries.append("illegal")

    with pytest.raises(TypeError):
        ledger.entries[0] = "illegal"
