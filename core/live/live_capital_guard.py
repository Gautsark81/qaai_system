from dataclasses import dataclass
from typing import Any

from core.capital.allocation_curves.engine import CapitalAllocationCurveEngine
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


# ======================================================
# Live Capital Guard Decision
# ======================================================

@dataclass(frozen=True)
class LiveCapitalDecision:
    allowed: bool
    max_multiplier: float
    reason: str
    diagnostics: dict[str, Any]


# ======================================================
# Live Capital Guard (FINAL EXECUTION GATE)
# ======================================================

class LiveCapitalGuard:
    """
    FINAL capital enforcement gate.

    HARD LAW:
    - Capital curves are binding
    - Risk & lifecycle dominate
    - No silent overrides
    """

    def __init__(self):
        self._curve_engine = CapitalAllocationCurveEngine()

    # --------------------------------------------------
    # PUBLIC ENTRY POINT
    # --------------------------------------------------

    def evaluate(
        self,
        *,
        strategy_id: str,
        lifecycle_state: LifecycleState,
        ssr: float,
        ssr_status: SSRStatus,
        health_score: float,
        health_status: HealthStatus,
        requested_multiplier: float,
    ) -> LiveCapitalDecision:

        diagnostics = {
            "strategy_id": strategy_id,
            "requested_multiplier": requested_multiplier,
            "lifecycle_state": lifecycle_state.value,
            "ssr": ssr,
            "ssr_status": ssr_status.value,
            "health_score": health_score,
            "health_status": health_status.value,
        }

        # ==================================================
        # 1️⃣ CAPITAL CURVE (HARD ENFORCEMENT)
        # ==================================================

        curve = self._curve_engine.compute(
            lifecycle_state=lifecycle_state,
            ssr=ssr,
            ssr_status=ssr_status,
            health_score=health_score,
            health_status=health_status,
        )

        diagnostics["capital_curve"] = {
            "eligible": curve.eligible,
            "allocation_pct": curve.allocation_pct,
            "reason": curve.reason,
            "version": curve.version,
        }

        if not curve.eligible:
            return LiveCapitalDecision(
                allowed=False,
                max_multiplier=0.0,
                reason=f"Blocked by capital curve: {curve.reason}",
                diagnostics=diagnostics,
            )

        # ==================================================
        # 2️⃣ ENFORCE ALLOCATION CAP
        # ==================================================

        enforced = min(
            requested_multiplier,
            curve.allocation_pct,
        )

        diagnostics["enforced_multiplier"] = enforced

        if enforced <= 0.0:
            return LiveCapitalDecision(
                allowed=False,
                max_multiplier=0.0,
                reason="Capital reduced to zero by curve",
                diagnostics=diagnostics,
            )

        if enforced < requested_multiplier:
            return LiveCapitalDecision(
                allowed=True,
                max_multiplier=enforced,
                reason=(
                    f"Capital capped by curve "
                    f"({requested_multiplier:.2f} → {enforced:.2f})"
                ),
                diagnostics=diagnostics,
            )

        # ==================================================
        # 3️⃣ PASS THROUGH
        # ==================================================

        return LiveCapitalDecision(
            allowed=True,
            max_multiplier=enforced,
            reason="Capital approved within curve",
            diagnostics=diagnostics,
        )
