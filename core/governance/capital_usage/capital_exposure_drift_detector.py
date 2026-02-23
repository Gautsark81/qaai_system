from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.governance.capital_usage.capital_exposure_reconciler import (
    CapitalExposureState,
)
from core.governance.reconstruction.governance_reconstruction_engine import (
    GovernanceState,
)


# ---------------------------------------------------------------------
# Drift Result
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CapitalExposureDriftResult:
    governance_id: str
    strategy_id: str
    drift_detected: bool
    drift_amount: float
    drift_ratio: float
    over_allocation: bool
    under_utilization: bool
    last_updated_at: datetime


# ---------------------------------------------------------------------
# Drift Detector
# ---------------------------------------------------------------------


class CapitalExposureDriftDetector:
    """
    Phase C5.3 — Detect drift between:

    - Governance authorized capital
    - Actual deployed capital

    Deterministic.
    Immutable.
    Pure.
    """

    UNDER_UTIL_THRESHOLD = 0.25  # <25% utilization triggers warning

    def detect(
        self,
        *,
        governance_state: GovernanceState,
        exposure_state: CapitalExposureState,
    ) -> CapitalExposureDriftResult:

        authorized_capital = governance_state.final_capital
        deployed_capital = exposure_state.deployed_capital

        drift_amount = deployed_capital - authorized_capital
        drift_ratio = (
            drift_amount / authorized_capital
            if authorized_capital > 0
            else 0.0
        )

        over_allocation = deployed_capital > authorized_capital
        under_utilization = (
            exposure_state.utilization_ratio < self.UNDER_UTIL_THRESHOLD
        )

        drift_detected = over_allocation

        return CapitalExposureDriftResult(
            governance_id=governance_state.governance_id,
            strategy_id=governance_state.strategy_id,
            drift_detected=drift_detected,
            drift_amount=drift_amount,
            drift_ratio=drift_ratio,
            over_allocation=over_allocation,
            under_utilization=under_utilization,
            last_updated_at=max(
                governance_state.last_updated_at,
                exposure_state.last_updated_at,
            ),
        )