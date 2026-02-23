# core/operator/escalation.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from core.operator.trust_score import OperatorTrustScore
from core.operator.abuse_signal import OperatorAbuseSignal


class EscalationLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


@dataclass(frozen=True)
class EscalationDecision:
    operator_id: str
    level: EscalationLevel
    reason: str
    requires_confirmation: bool
    requires_delay: bool
    audit_prominence: str  # "normal", "elevated", "board"


# core/operator/escalation.py (continued)

def compute_escalation(
    trust: OperatorTrustScore,
    abuse_signal: Optional[OperatorAbuseSignal],
) -> EscalationDecision:
    """
    Computes escalation level based on trust and abuse signals.
    Never blocks execution.
    """

    # Default: GREEN
    level = EscalationLevel.GREEN
    reason = "normal operation"
    requires_confirmation = False
    requires_delay = False
    audit_prominence = "normal"

    # Trust-based escalation
    if trust.trust < 0.8:
        level = EscalationLevel.YELLOW
        reason = "reduced trust due to recent activity"
        requires_confirmation = True
        audit_prominence = "elevated"

    if trust.trust < 0.6:
        level = EscalationLevel.ORANGE
        reason = "low trust from fatigue or overrides"
        requires_confirmation = True
        requires_delay = True
        audit_prominence = "elevated"

    # Abuse-based escalation dominates trust
    if abuse_signal is not None and abuse_signal.confidence >= 0.7:
        level = EscalationLevel.RED
        reason = "override abuse pattern detected"
        requires_confirmation = True
        requires_delay = True
        audit_prominence = "board"

    return EscalationDecision(
        operator_id=trust.operator_id,
        level=level,
        reason=reason,
        requires_confirmation=requires_confirmation,
        requires_delay=requires_delay,
        audit_prominence=audit_prominence,
    )
