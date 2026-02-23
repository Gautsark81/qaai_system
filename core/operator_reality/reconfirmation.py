from dataclasses import dataclass
from .models import OperatorIntent


@dataclass(frozen=True)
class ReconfirmationRequirement:
    """
    Represents the requirement for operator reconfirmation.

    This is a governance signal only.
    It does NOT enforce execution changes.
    """

    intent: OperatorIntent
    required: bool
    reason: str


class OperatorReconfirmationEvaluator:
    """
    Determines whether operator reconfirmation is required.

    No execution authority.
    No system mutation.
    """

    @staticmethod
    def evaluate(
        *,
        intent: OperatorIntent,
        expired: bool,
        warning: bool,
    ) -> ReconfirmationRequirement:
        if expired:
            return ReconfirmationRequirement(
                intent=intent,
                required=True,
                reason="OPERATOR_INTENT_EXPIRED",
            )

        if warning:
            return ReconfirmationRequirement(
                intent=intent,
                required=True,
                reason="OPERATOR_FATIGUE_WARNING",
            )

        return ReconfirmationRequirement(
            intent=intent,
            required=False,
            reason="INTENT_STILL_VALID",
        )
