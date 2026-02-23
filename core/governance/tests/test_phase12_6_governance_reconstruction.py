# core/governance/tests/test_phase12_6_governance_reconstruction.py

from datetime import datetime, timezone

from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger
from core.capital.ledger.capital_scaling_ledger_entry import CapitalScalingLedgerEntry
from core.capital.throttle.ledger.capital_throttle_ledger import CapitalThrottleLedger
from core.capital.throttle.ledger.capital_throttle_ledger_entry import CapitalThrottleLedgerEntry

from core.governance.reconstruction import GovernanceReconstructionEngine


def test_governance_reconstruction_minimal_chain():
    """
    Phase 12.6.1

    Reconstruct governance state from:
    - scaling ledger
    - throttle ledger
    using a shared governance_id
    """

    gov_id = "gov-001"
    ts = datetime.now(timezone.utc)

    scaling_ledger = CapitalScalingLedger()
    throttle_ledger = CapitalThrottleLedger()

    scaling_ledger.append(
        CapitalScalingLedgerEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    throttle_ledger.append(
        CapitalThrottleLedgerEntry(
            strategy_id="STRAT-1",
            throttle_factor=1.0,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    engine = GovernanceReconstructionEngine(
        scaling_ledger=scaling_ledger,
        throttle_ledger=throttle_ledger,
    )

    state = engine.reconstruct(governance_id=gov_id)

    assert state.governance_id == gov_id
    assert state.strategy_id == "STRAT-1"
    assert state.final_capital == 1_200_000
    assert state.throttle_factor == 1.0
