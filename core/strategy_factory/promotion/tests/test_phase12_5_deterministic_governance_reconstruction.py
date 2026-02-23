from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger
from core.capital.throttle.ledger.capital_throttle_ledger import (
    CapitalThrottleLedger,
)


def test_governance_history_can_be_reconstructed():
    scaling_ledger = CapitalScalingLedger()
    throttle_ledger = CapitalThrottleLedger()

    scaling_ids = {e.governance_id for e in scaling_ledger.entries}
    throttle_ids = {e.governance_id for e in throttle_ledger.entries}

    # Throttle decisions must never exist without scaling lineage
    assert throttle_ids.issubset(scaling_ids)
