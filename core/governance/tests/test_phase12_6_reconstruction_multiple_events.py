from datetime import datetime, timezone

import pytest

from core.governance.reconstruction import GovernanceReconstructionEngine
from core.capital.ledger.capital_scaling_ledger_entry import CapitalScalingLedgerEntry
from core.capital.throttle.ledger.capital_throttle_ledger import CapitalThrottleLedger
from core.capital.throttle.ledger.capital_throttle_ledger_entry import CapitalThrottleLedgerEntry
from core.capital.ledger.capital_scaling_ledger import CapitalScalingLedger


def test_reconstruction_with_multiple_scaling_and_throttle_events():
    """
    Phase 12.6.2
    Governance reconstruction must deterministically resolve multiple
    scaling + throttle events under the same governance chain.

    Semantics:
    - Last event (by timestamp) wins per dimension
    - Ordering of ledger insertion MUST NOT matter
    - Output must be immutable
    """

    gov_id = "gov-multi-001"

    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    t3 = datetime(2026, 1, 3, tzinfo=timezone.utc)
    t4 = datetime(2026, 1, 4, tzinfo=timezone.utc)

    # --- Scaling ledger (out of order insertion) ---
    scaling_ledger = CapitalScalingLedger()

    scaling_ledger.append(
        CapitalScalingLedgerEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,
            decision_reason="SCALE_UP_1",
            decision_checksum="chk-1",
            governance_id=gov_id,
            timestamp=t2,
        )
    )

    scaling_ledger.append(
        CapitalScalingLedgerEntry(
            strategy_id="STRAT-1",
            previous_capital=1_200_000,
            new_capital=900_000,
            scale_factor=0.75,
            decision_reason="SCALE_DOWN",
            decision_checksum="chk-2",
            governance_id=gov_id,
            timestamp=t4,
        )
    )

    scaling_ledger.append(
        CapitalScalingLedgerEntry(
            strategy_id="STRAT-1",
            previous_capital=900_000,
            new_capital=1_050_000,
            scale_factor=1.1667,
            decision_reason="SCALE_UP_2",
            decision_checksum="chk-3",
            governance_id=gov_id,
            timestamp=t3,
        )
    )

    # --- Throttle ledger (also out of order) ---
    throttle_ledger = CapitalThrottleLedger()

    throttle_ledger.append(
        CapitalThrottleLedgerEntry(
            strategy_id="STRAT-1",
            throttle_level=0.8,
            reason="VOLATILITY_SPIKE",
            decision_checksum="thr-1",
            governance_id=gov_id,
            timestamp=t1,
        )
    )

    throttle_ledger.append(
        CapitalThrottleLedgerEntry(
            strategy_id="STRAT-1",
            throttle_level=0.5,
            reason="DRAWDOWN",
            decision_checksum="thr-2",
            governance_id=gov_id,
            timestamp=t3,
        )
    )

    throttle_ledger.append(
        CapitalThrottleLedgerEntry(
            strategy_id="STRAT-1",
            throttle_level=1.0,
            reason="NO_THROTTLE",
            decision_checksum="thr-3",
            governance_id=gov_id,
            timestamp=t4,
        )
    )

    # --- Reconstruction ---
    engine = GovernanceReconstructionEngine(
        scaling_ledger=scaling_ledger,
        throttle_ledger=throttle_ledger,
    )

    state = engine.reconstruct(governance_id=gov_id)

    # --- Assertions (LAW) ---
    # Scaling: last timestamp (t4) wins
    assert state.capital_scale_factor == 0.75
    assert state.capital_scale_reason == "SCALE_DOWN"

    # Throttle: last timestamp (t4) wins
    assert state.throttle_level == 1.0
    assert state.throttle_reason == "NO_THROTTLE"

    # Governance id preserved
    assert state.governance_id == gov_id

    # Deterministic timestamp resolution
    assert state.last_updated_at == t4

    # Output must be immutable
    with pytest.raises(AttributeError):
        state.capital_scale_factor = 999
