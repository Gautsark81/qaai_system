from __future__ import annotations

from datetime import datetime
import hashlib

from core.strategy_factory.promotion.admission.live_admission_decision import (
    LiveAdmissionDecision,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


class LiveAdmissionGate:
    """
    Final gate before FULL LIVE capital admission.

    STRICT CONTRACT:
    - Deterministic
    - No wall-clock access
    - No hidden mutation
    - Replay-safe
    - Governance-auditable

    Time MUST be injected.
    """

    # ===============================================================
    # PUBLIC API
    # ===============================================================

    def evaluate(
        self,
        *,
        strategy,
        ssr_metrics,
        risk_envelope,
        now: datetime,
    ) -> LiveAdmissionDecision:
        """
        Evaluate whether strategy may be promoted from TINY_LIVE → LIVE.

        Deterministic contract:
        - `now` must be injected
        - No datetime.now() allowed
        """

        # -------------------------------
        # State validation
        # -------------------------------
        if not hasattr(strategy, "state"):
            return self._deny(
                reason="invalid strategy state",
                explanation="Strategy missing state",
                next_state=None,
                now=now,
            )

        if strategy.state != PromotionState.TINY_LIVE:
            return self._deny(
                reason="invalid promotion state",
                explanation="Strategy not in TINY_LIVE state",
                next_state=None,
                now=now,
            )

        # -------------------------------
        # Authority checks
        # -------------------------------
        if not strategy.capital_authority:
            return self._deny(
                reason="capital authority missing",
                explanation="Capital authority missing",
                next_state=None,
                now=now,
            )

        if not strategy.execution_authority:
            return self._deny(
                reason="execution authority missing",
                explanation="Execution authority missing",
                next_state=None,
                now=now,
            )

        if strategy.operator_veto:
            return self._deny(
                reason="operator veto active",
                explanation="Operator veto active",
                next_state=None,
                now=now,
            )

        # -------------------------------
        # SSR eligibility
        # -------------------------------
        if not ssr_metrics.is_live_eligible():
            return self._deny(
                reason="ssr below threshold",
                explanation="SSR below governed live threshold",
                next_state=None,
                now=now,
            )

        # -------------------------------
        # Risk envelope validation
        # -------------------------------
        if str(risk_envelope) != "VALID":
            return self._deny(
                reason="risk violation",
                explanation="Risk envelope not approved for live",
                next_state=None,
                now=now,
            )

        # -------------------------------
        # SUCCESS → FULL LIVE
        # -------------------------------
        checksum = self._checksum(strategy, ssr_metrics, risk_envelope)

        return LiveAdmissionDecision(
            allowed=True,
            reason="live admission approved",
            explanation="Strategy approved for full live capital",
            next_state=PromotionState.LIVE,
            evidence_checksum=checksum,
            timestamp=now,
        )

    # ===============================================================
    # INTERNAL HELPERS
    # ===============================================================

    def _deny(
        self,
        *,
        reason: str,
        explanation: str,
        next_state,
        now: datetime,
    ) -> LiveAdmissionDecision:
        """
        Deterministic denial path.
        """

        checksum = hashlib.sha256(
            f"{reason}|{explanation}".encode()
        ).hexdigest()

        return LiveAdmissionDecision(
            allowed=False,
            reason=reason,
            explanation=explanation,
            next_state=next_state,
            evidence_checksum=checksum,
            timestamp=now,
        )

    def _checksum(self, strategy, ssr_metrics, risk_envelope) -> str:
        """
        Deterministic governance checksum.
        """

        payload = (
            f"{strategy.strategy_id}|"
            f"{strategy.state}|"
            f"{strategy.capital_authority}|"
            f"{strategy.execution_authority}|"
            f"{strategy.operator_veto}|"
            f"{ssr_metrics.ssr}|"
            f"{risk_envelope}"
        )

        return hashlib.sha256(payload.encode()).hexdigest()