from datetime import datetime, timezone

from core.governance.enforcement.auto_throttle_enforcer import (
    AutoThrottleEnforcer,
)
from core.governance.reconstruction.governance_reconstruction_engine import (
    GovernanceState,
)
from core.governance.drift.capital_exposure_drift import (
    CapitalExposureDriftResult,
)
from core.strategy_factory.capital.ledger.throttle_ledger import (
    CapitalThrottleLedger,
)


def test_auto_throttle_triggers_on_over_allocation():

    now = datetime.now(timezone.utc)

    state = GovernanceState(
        governance_id="gov-auto-1",
        strategy_id="STRAT-1",
        final_capital=1_000_000,
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,
        throttle_reason="NONE",
        last_updated_at=now,
    )

    drift = CapitalExposureDriftResult(
        over_allocated=True,
        under_utilized=False,
        utilization_ratio=1.25,
        drift_amount=250_000,
    )

    ledger = CapitalThrottleLedger()

    enforcer = AutoThrottleEnforcer()

    result = enforcer.enforce(
        governance_state=state,
        drift_result=drift,
        throttle_ledger=ledger,
    )

    assert result.enforced is True
    assert result.throttle_level == 0.75
    assert len(ledger.entries) == 1


def test_auto_throttle_does_not_trigger_when_safe():

    now = datetime.now(timezone.utc)

    state = GovernanceState(
        governance_id="gov-auto-2",
        strategy_id="STRAT-2",
        final_capital=1_000_000,
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,
        throttle_reason="NONE",
        last_updated_at=now,
    )

    drift = CapitalExposureDriftResult(
        over_allocated=False,
        under_utilized=False,
        utilization_ratio=0.8,
        drift_amount=0,
    )

    ledger = CapitalThrottleLedger()

    enforcer = AutoThrottleEnforcer()

    result = enforcer.enforce(
        governance_state=state,
        drift_result=drift,
        throttle_ledger=ledger,
    )

    assert result.enforced is False
    assert len(ledger.entries) == 0