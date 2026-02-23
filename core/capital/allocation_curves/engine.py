from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus

from .curves import AllocationCurves
from .contracts import CapitalCurveSnapshot
from .versions import CAPITAL_CURVE_V1


class CapitalAllocationCurveEngine:
    """
    Computes advisory capital allocation fraction.
    """

    def compute(
        self,
        *,
        lifecycle_state: LifecycleState,
        ssr: float,
        ssr_status: SSRStatus,
        health_score: float,
        health_status: HealthStatus,
    ) -> CapitalCurveSnapshot:

        # ---- Lifecycle gate ----
        if lifecycle_state in {
            LifecycleState.CANDIDATE,
            LifecycleState.PAPER,
            LifecycleState.RETIRED,
        }:
            return CapitalCurveSnapshot(
                eligible=False,
                allocation_pct=0.0,
                reason="Lifecycle state not eligible",
                version=CAPITAL_CURVE_V1,
            )

        # ---- Hard safety ----
        if ssr_status == SSRStatus.FAILING:
            return CapitalCurveSnapshot(
                eligible=False,
                allocation_pct=0.0,
                reason="SSR FAILING",
                version=CAPITAL_CURVE_V1,
            )

        if health_status == HealthStatus.CRITICAL:
            return CapitalCurveSnapshot(
                eligible=False,
                allocation_pct=0.0,
                reason="Health CRITICAL",
                version=CAPITAL_CURVE_V1,
            )

        # ---- Base curve ----
        base = AllocationCurves.base_curve(
            ssr=ssr,
            health=health_score,
        )

        # ---- DEGRADED throttle ----
        if lifecycle_state == LifecycleState.DEGRADED:
            base *= 0.25

        return CapitalCurveSnapshot(
            eligible=True,
            allocation_pct=round(base, 4),
            reason="Normal allocation",
            version=CAPITAL_CURVE_V1,
        )
