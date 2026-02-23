from dataclasses import dataclass
from typing import Union

from core.execution.broker_response.contracts import BrokerDecision
from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.retry_integration import (
    attach_retry_recommendation,
)


@dataclass(frozen=True)
class BrokerFailurePolicy:
    retry_allowed: bool
    escalate: bool
    replay_safe: bool


_POLICY_MATRIX = {
    BrokerDecision.ACCEPTED: BrokerFailurePolicy(
        retry_allowed=False,
        escalate=False,
        replay_safe=True,
    ),
    BrokerDecision.REJECTED: BrokerFailurePolicy(
        retry_allowed=False,
        escalate=False,
        replay_safe=True,
    ),
    BrokerDecision.PARTIAL_FILL: BrokerFailurePolicy(
        retry_allowed=False,
        escalate=True,
        replay_safe=False,
    ),
    BrokerDecision.TRANSIENT_FAILURE: BrokerFailurePolicy(
        retry_allowed=True,
        escalate=False,
        replay_safe=False,
    ),
    BrokerDecision.UNKNOWN_STATE: BrokerFailurePolicy(
        retry_allowed=False,
        escalate=True,
        replay_safe=False,
    ),
}


def policy_for(
    subject: Union[BrokerResponse, BrokerDecision],
) -> BrokerFailurePolicy:
    """
    Derive broker failure policy.

    Accepts:
    - BrokerResponse (preferred)
    - BrokerDecision (test compatibility)

    Pure. Deterministic. Governance-only.
    """

    if isinstance(subject, BrokerDecision):
        return _POLICY_MATRIX[subject]

    base_policy = _POLICY_MATRIX[subject.decision]

    retry_info = attach_retry_recommendation(subject)

    if retry_info.retry_decision.value != "RETRYABLE":
        return base_policy

    return BrokerFailurePolicy(
        retry_allowed=True,
        escalate=base_policy.escalate,
        replay_safe=base_policy.replay_safe,
    )


__all__ = ["BrokerFailurePolicy", "policy_for"]
