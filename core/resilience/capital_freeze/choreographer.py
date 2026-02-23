# core/resilience/capital_freeze/choreographer.py
from core.resilience.extreme_events.models import ExtremeEventType, ExtremeEventClassification
from core.resilience.capital_freeze.models import (
    CapitalFreezeDecision,
    CapitalControlAction,
)


class CapitalFreezeChoreographer:
    """
    Maps extreme event classifications to capital control actions.

    NOTE:
    - No enforcement
    - No execution
    - Pure decision choreography
    """

    def decide(
        self,
        *,
        classification: ExtremeEventClassification,
    ) -> CapitalFreezeDecision:
        etype = classification.event_type
        severity = classification.severity

        if etype == ExtremeEventType.NORMAL:
            return CapitalFreezeDecision(
                action=CapitalControlAction.NONE,
                severity=0.0,
                reason="normal conditions",
                evidence=classification.evidence,
            )

        if etype == ExtremeEventType.VOLATILITY_SPIKE:
            return CapitalFreezeDecision(
                action=CapitalControlAction.THROTTLE_NEW_TRADES,
                severity=severity,
                reason="volatility spike detected",
                evidence=classification.evidence,
            )

        if etype in (
            ExtremeEventType.MARKET_CRASH,
            ExtremeEventType.LIQUIDITY_FREEZE,
        ):
            return CapitalFreezeDecision(
                action=CapitalControlAction.FREEZE_NEW_TRADES,
                severity=severity,
                reason=f"{etype.value} detected",
                evidence=classification.evidence,
            )

        if etype == ExtremeEventType.SYSTEM_ANOMALY:
            return CapitalFreezeDecision(
                action=CapitalControlAction.FULL_SYSTEM_FREEZE,
                severity=severity,
                reason="system anomaly detected",
                evidence=classification.evidence,
            )

        # Fallback safety
        return CapitalFreezeDecision(
            action=CapitalControlAction.FULL_SYSTEM_FREEZE,
            severity=1.0,
            reason="unclassified extreme event",
            evidence=classification.evidence,
        )
