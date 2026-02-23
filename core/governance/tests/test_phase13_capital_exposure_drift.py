from datetime import datetime, timezone

from core.governance.capital_usage.capital_exposure_drift_detector import (
    CapitalExposureDriftDetector,
)
from core.governance.capital_usage.capital_exposure_reconciler import (
    CapitalExposureState,
)
from core.governance.reconstruction.governance_reconstruction_engine import (
    GovernanceState,
)


def test_over_allocation_detected():
    now = datetime.now(timezone.utc)

    governance_state = GovernanceState(
        governance_id="gov-1",
        strategy_id="STRAT-1",
        final_capital=1_000_000,
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,  # REQUIRED
        throttle_reason="NONE",
        last_updated_at=now,
    )

    exposure_state = CapitalExposureState(
        strategy_id="STRAT-1",
        governance_id="gov-1",
        allocated_capital=1_000_000,
        deployed_capital=1_200_000,
        realized_pnl=0,
        utilization_ratio=1.2,
        over_allocated=True,
        last_updated_at=now,
    )

    detector = CapitalExposureDriftDetector()

    result = detector.detect(
        governance_state=governance_state,
        exposure_state=exposure_state,
    )

    assert result.drift_detected is True
    assert result.over_allocation is True
    assert result.drift_amount == 200_000


def test_under_utilization_warning_only():
    now = datetime.now(timezone.utc)

    governance_state = GovernanceState(
        governance_id="gov-2",
        strategy_id="STRAT-2",
        final_capital=1_000_000,
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,  # REQUIRED
        throttle_reason="NONE",
        last_updated_at=now,
    )

    exposure_state = CapitalExposureState(
        strategy_id="STRAT-2",
        governance_id="gov-2",
        allocated_capital=1_000_000,
        deployed_capital=100_000,
        realized_pnl=0,
        utilization_ratio=0.1,
        over_allocated=False,
        last_updated_at=now,
    )

    detector = CapitalExposureDriftDetector()

    result = detector.detect(
        governance_state=governance_state,
        exposure_state=exposure_state,
    )

    assert result.drift_detected is False
    assert result.under_utilization is True