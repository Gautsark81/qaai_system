from dataclasses import dataclass
from .incident_types import IncidentType


@dataclass(frozen=True)
class KillDecision:
    """
    Governance-only kill decision.

    This does NOT execute the kill.
    It only states whether escalation is required.
    """

    escalate: bool
    authority: str
    reason: str


class KillHierarchyPolicy:
    """
    Determines escalation authority based on incident type.

    No execution.
    No state mutation.
    """

    @staticmethod
    def decide(*, incident_type: IncidentType) -> KillDecision:
        if incident_type in {
            IncidentType.CAPITAL_BREACH,
            IncidentType.GOVERNANCE_VIOLATION,
        }:
            return KillDecision(
                escalate=True,
                authority="HARD_KILL",
                reason=incident_type.value,
            )

        if incident_type in {
            IncidentType.OPERATOR_ABSENCE,
            IncidentType.EXECUTION_INVARIANT,
        }:
            return KillDecision(
                escalate=True,
                authority="SOFT_KILL",
                reason=incident_type.value,
            )

        return KillDecision(
            escalate=False,
            authority="NO_KILL",
            reason="NON_FATAL_INCIDENT",
        )
