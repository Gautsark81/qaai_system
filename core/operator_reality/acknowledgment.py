from .models import OperatorIntent, OperatorAcknowledgment


class OperatorAcknowledgmentService:
    """
    Governance-only acknowledgment service.

    This service:
    - converts operator intent into an immutable acknowledgment
    - does NOT write to disk
    - does NOT invoke execution
    - does NOT modify system state

    Persistence is intentionally external (evidence layer).
    """

    @staticmethod
    def acknowledge(
        *,
        intent: OperatorIntent,
        evidence_id: str,
    ) -> OperatorAcknowledgment:
        if not isinstance(intent, OperatorIntent):
            raise TypeError("intent must be an OperatorIntent")

        if not evidence_id:
            raise ValueError("evidence_id must be provided")

        return OperatorAcknowledgment(
            intent=intent,
            acknowledged=True,
            evidence_id=evidence_id,
        )
