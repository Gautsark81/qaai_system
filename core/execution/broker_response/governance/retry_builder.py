from core.execution.broker_response.governance.classifier import ResponseClassifier
from core.execution.broker_response.governance.retry_decision import RetryDecision
from core.execution.broker_response.governance.retry_recommendation import RetryRecommendation


# ---------------------------------------------------------------------
# GOVERNANCE RECOMMENDATION BUILDER (PURE)
# ---------------------------------------------------------------------
def build_governance_recommendation(resp):
    """
    Build a deterministic governance recommendation.

    Governance-only logic.
    No authority. No side effects.
    """

    outcome = ResponseClassifier.classify(resp)

    # Governance rule:
    # Any transient infrastructure failure is retryable,
    # regardless of rejection status.
    rejection_text = (resp.rejection_reason or "").lower()

    is_transient = (
        "temporary" in rejection_text
        or "timeout" in rejection_text
        or "network" in rejection_text
        or "rate" in rejection_text
        or outcome.name == "TRANSIENT_FAILURE"
    )

    if is_transient:
        decision = RetryDecision.RETRYABLE
        reason = "TRANSIENT_FAILURE"
    else:
        decision = RetryDecision.NON_RETRYABLE
        reason = "NON_RETRYABLE_OUTCOME"

    return RetryRecommendation(
        outcome=outcome,
        retry_decision=decision,
        response_hash=resp.response_hash,
        reason=reason,
        timestamp=resp.timestamp,
    )


# Backward-compatible export for tests
build_retry_recommendation = build_governance_recommendation


__all__ = ["build_retry_recommendation"]
