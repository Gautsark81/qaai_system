from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_decision import RetryDecision
from core.execution.broker_response.governance.retry_policy import retry_decision_for


def test_retry_policy_matrix_is_complete():
    """
    Every BrokerOutcome must map to exactly one RetryDecision.
    """

    for outcome in BrokerOutcome:
        decision = retry_decision_for(outcome)
        assert isinstance(decision, RetryDecision)
