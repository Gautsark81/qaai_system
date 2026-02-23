from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger
from core.capital.throttle.ledger.capital_throttle_ledger import (
    CapitalThrottleLedger,
)
from core.capital.ledger.capital_scaling_ledger_entry import (
    CapitalScalingLedgerEntry,
)
from core.capital.throttle.ledger.capital_throttle_ledger_entry import (
    CapitalThrottleLedgerEntry,
)


def test_ledgers_cross_reference_governance_id():
    scaling_ledger = CapitalScalingLedger()
    throttle_ledger = CapitalThrottleLedger()

    scaling_entry = CapitalScalingLedgerEntry(
        strategy_id="STRAT-1",
        previous_capital=1_000_000,
        new_capital=1_200_000,
        scale_factor=1.2,
        governance_id="gov-777",
    )

    throttle_entry = CapitalThrottleLedgerEntry(
        strategy_id="STRAT-1",
        throttle_factor=1.0,
        governance_id="gov-777",
    )

    scaling_ledger.append(scaling_entry)
    throttle_ledger.append(throttle_entry)

    assert scaling_ledger.entries[0].governance_id == throttle_ledger.entries[0].governance_id
