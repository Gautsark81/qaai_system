from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.outcome import BrokerOutcome


def classify_response(response: BrokerResponse) -> BrokerOutcome:
    """
    Deterministic, broker-agnostic interpretation rules.

    NO execution authority.
    NO retries.
    NO mutation.
    """

    # -----------------------------
    # Accepted fills
    # -----------------------------
    if response.decision == "ACCEPTED":
        if response.filled_quantity > 0:
            return BrokerOutcome.SUCCESS
        return BrokerOutcome.REJECTED

    # -----------------------------
    # Rejections
    # -----------------------------
    if response.decision == "REJECTED":
        reason = (response.rejection_reason or "").lower()

        if any(x in reason for x in ("timeout", "temporary", "network", "retry")):
            return BrokerOutcome.RETRYABLE_FAILURE

        return BrokerOutcome.TERMINAL_FAILURE

    # -----------------------------
    # Fallback
    # -----------------------------
    return BrokerOutcome.UNKNOWN
