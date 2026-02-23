from datetime import datetime
from typing import Callable

from .decision import RetrainingDecision
from .planner import RetrainingPlan
from .audit import RetrainingAuditEvent
from .regime import MarketRegime


class RetrainingDecisionEngine:
    """
    Determines whether retraining should be triggered and produces a plan.
    """

    def __init__(
        self,
        *,
        regime_classifier: Callable,
        audit_sink,
        clock,
        max_psi: float = 0.2,
        max_shadow_divergence: float = 0.25,
    ):
        self.regime_classifier = regime_classifier
        self.audit_sink = audit_sink
        self.clock = clock
        self.max_psi = max_psi
        self.max_shadow_divergence = max_shadow_divergence

    def evaluate(
        self,
        *,
        model_id: str,
        signals,
        market_snapshot,
    ) -> tuple[RetrainingDecision, RetrainingPlan | None]:

        regime = self.regime_classifier(market_snapshot)
        reasons = []

        if signals.decay_detected:
            reasons.append("decay_detected")

        if signals.feature_drift_psi > self.max_psi:
            reasons.append("feature_drift")

        if signals.shadow_divergence > self.max_shadow_divergence:
            reasons.append("shadow_divergence")

        if not reasons:
            return (
                RetrainingDecision(False, [], regime),
                None,
            )

        plan = RetrainingPlan(
            regime=regime,
            lookback_days=120 if regime == MarketRegime.HIGH_VOL else 250,
            model_family="gradient_boosted_trees",
            featureset="v2",
            reasons=reasons,
        )

        self.audit_sink.emit(
            RetrainingAuditEvent(
                model_id=model_id,
                regime=regime,
                reasons=reasons,
                timestamp=self.clock.utcnow(),
            )
        )

        return (
            RetrainingDecision(True, reasons, regime),
            plan,
        )
