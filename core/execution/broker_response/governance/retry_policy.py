from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_decision import RetryDecision


# ---------------------------------------------------------------------
# AUTHORITATIVE RETRY ELIGIBILITY MATRIX
# ---------------------------------------------------------------------
# Rules:
# - SUCCESS           → never retry
# - REJECTED          → never retry (business / broker rejection)
# - TERMINAL_FAILURE  → never retry (hard failure)
# - RETRYABLE_FAILURE → retry allowed
#
# IMPORTANT:
# - No execution
# - No retry logic
# - No timing / sleep
# - Classification ONLY
# ---------------------------------------------------------------------
_RETRY_MATRIX = {
    BrokerOutcome.SUCCESS: RetryDecision.NON_RETRYABLE,
    BrokerOutcome.REJECTED: RetryDecision.NON_RETRYABLE,
    BrokerOutcome.TERMINAL_FAILURE: RetryDecision.NON_RETRYABLE,
    BrokerOutcome.RETRYABLE_FAILURE: RetryDecision.RETRYABLE,
}


def retry_decision_for(outcome: BrokerOutcome) -> RetryDecision:
    """
    Determine retry eligibility for a given BrokerOutcome.

    Characteristics:
    - Pure
    - Deterministic
    - Governance-only
    - No execution authority
    """

    # Governance-safe default: never retry unless explicitly allowed
    return _RETRY_MATRIX.get(outcome, RetryDecision.NON_RETRYABLE)


__all__ = ["retry_decision_for"]
