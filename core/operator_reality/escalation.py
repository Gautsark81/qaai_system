from dataclasses import dataclass
from .reconfirmation import ReconfirmationRequirement


@dataclass(frozen=True)
class OperatorEscalationDecision:
    """
    Governance-only escalation outcome.

    This does NOT trigger execution changes.
    Downstream systems may consume this as advisory input.
    """

    escalate: bool
    reason: str


class OperatorEscalationPolicy:
    """
    Converts reconfirmation requirements into escalation signals.

    Escalation here means:
    - require human attention
    - recommend safe-state dominance
    """

    @staticmethod
    def decide(
        *, reconfirmation: ReconfirmationRequirement
    ) -> OperatorEscalationDecision:
        if reconfirmation.required:
            return OperatorEscalationDecision(
                escalate=True,
                reason=reconfirmation.reason,
            )

        return OperatorEscalationDecision(
            escalate=False,
            reason="NO_ESCALATION_REQUIRED",
        )
