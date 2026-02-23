from datetime import datetime
from typing import Optional, Tuple

from core.lifecycle.contracts.state import LifecycleState
from core.lifecycle.contracts.enums import TransitionReason
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


class LifecycleRules:
    """
    Canonical lifecycle transition rules.

    RULES ARE:
    - Pure (no side effects)
    - Deterministic
    - Replay-safe

    ENGINE ENFORCES:
    - Monotonicity (no backward / no skip)
    - Governance
    - Exactly-once emission
    """

    def __init__(
        self,
        *,
        min_live_days: int = 3,
        min_recovery_days: int = 5,
    ):
        self.min_live_days = min_live_days
        self.min_recovery_days = min_recovery_days

    def evaluate(
        self,
        *,
        current_state: LifecycleState,
        since: datetime,
        now: datetime,
        ssr_status: SSRStatus,
        health_status: HealthStatus,
        operator_override: Optional[LifecycleState] = None,
        execution_reason: Optional[str] = None,
    ) -> Tuple[Optional[LifecycleState], Optional[TransitionReason]]:

        # --------------------------------------------------
        # TERMINAL
        # --------------------------------------------------
        if current_state == LifecycleState.RETIRED:
            return None, None

        days_in_state = (now - since).days

        # --------------------------------------------------
        # OPERATOR OVERRIDE (ENGINE WILL VALIDATE)
        # --------------------------------------------------
        if operator_override is not None:
            return operator_override, TransitionReason.OPERATOR_OVERRIDE

        # --------------------------------------------------
        # EXECUTION QUALITY (LIVE ONLY)
        # --------------------------------------------------
        if current_state == LifecycleState.LIVE:
            if execution_reason in {
                "EXECUTION_OVERFILL",
                "EXECUTION_UNDERFILL",
            }:
                return LifecycleState.DEGRADED, TransitionReason.EXECUTION_QUALITY

        if execution_reason == "EXECUTION_BREACH":
            return LifecycleState.RETIRED, TransitionReason.EXECUTION_BREACH

        # --------------------------------------------------
        # PROMOTIONS (FORWARD ONLY)
        # --------------------------------------------------

        # CANDIDATE → PAPER
        # Tests REQUIRE:
        # - SSR >= STABLE
        # - HEALTHY
        # - No time gating
        if current_state == LifecycleState.CANDIDATE:
            if (
                ssr_status in {SSRStatus.STABLE, SSRStatus.STRONG}
                and health_status == HealthStatus.HEALTHY
            ):
                return LifecycleState.PAPER, TransitionReason.SSR_STRONG
            return None, None

        # PAPER → LIVE (eligibility only; governance enforced by engine)
        if current_state == LifecycleState.PAPER:
            if (
                ssr_status == SSRStatus.STRONG
                and health_status == HealthStatus.HEALTHY
                and days_in_state >= self.min_live_days
            ):
                return LifecycleState.LIVE, TransitionReason.SSR_STRONG
            return None, None

        # --------------------------------------------------
        # LIVE STATE (DEGRADATION ONLY)
        # --------------------------------------------------
        if current_state == LifecycleState.LIVE:
            if ssr_status in {SSRStatus.WEAK, SSRStatus.FAILING}:
                return LifecycleState.DEGRADED, TransitionReason.SSR_WEAK

            if health_status == HealthStatus.DEGRADED:
                return LifecycleState.DEGRADED, TransitionReason.HEALTH_DEGRADED

            return None, None

        # --------------------------------------------------
        # DEGRADED STATE
        # --------------------------------------------------
        if current_state == LifecycleState.DEGRADED:
            if ssr_status == SSRStatus.FAILING:
                return LifecycleState.RETIRED, TransitionReason.SSR_FAILING

            if health_status == HealthStatus.CRITICAL:
                return LifecycleState.RETIRED, TransitionReason.HEALTH_CRITICAL

            # Explicit recovery (allowed, but engine enforces monotonicity)
            if (
                ssr_status == SSRStatus.STRONG
                and health_status == HealthStatus.HEALTHY
                and days_in_state >= self.min_recovery_days
            ):
                return LifecycleState.LIVE, TransitionReason.SSR_STRONG

            return None, None

        # --------------------------------------------------
        # DEFAULT
        # --------------------------------------------------
        return None, None
