from datetime import datetime, timezone

from core.strategy_factory.promotion.gating.live_capital_gate_decision import (
    LiveCapitalGateDecision,
)
from core.strategy_factory.promotion.gating.live_capital_gate_reason import (
    LiveCapitalGateReason,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


class LiveCapitalGate:
    """
    Governance-only gate.
    NO execution authority.
    NO capital authority.
    Deterministic.
    """

    def evaluate(
        self,
        *,
        strategy_state: PromotionState,
        ssr_metrics,
        risk_envelope,
    ) -> LiveCapitalGateDecision:

        now = datetime.fromtimestamp(0, tz=timezone.utc)

        if strategy_state != PromotionState.TINY_LIVE:
            return LiveCapitalGateDecision(
                allowed=False,
                reason=LiveCapitalGateReason.INVALID_PROMOTION_STATE,
                explanation="Strategy not in TINY_LIVE state",
                timestamp=now,
            )

        if not ssr_metrics.is_live_eligible():
            return LiveCapitalGateDecision(
                allowed=False,
                reason=LiveCapitalGateReason.SSR_BELOW_THRESHOLD,
                explanation="SSR below governed live threshold",
                timestamp=now,
            )

        if str(risk_envelope) != "VALID":
            return LiveCapitalGateDecision(
                allowed=False,
                reason=LiveCapitalGateReason.RISK_ENVELOPE_VIOLATION,
                explanation="Risk envelope violation",
                timestamp=now,
            )

        return LiveCapitalGateDecision(
            allowed=True,
            reason=LiveCapitalGateReason.SSR_BELOW_THRESHOLD,  # placeholder, not used when allowed
            explanation="Eligible for governed live capital",
            timestamp=now,
        )
