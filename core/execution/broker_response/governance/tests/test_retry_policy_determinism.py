from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_policy import retry_decision_for


def test_retry_policy_is_deterministic():
    """
    Same input must always produce the same output.
    """

    for outcome in BrokerOutcome:
        d1 = retry_decision_for(outcome)
        d2 = retry_decision_for(outcome)
        assert d1 == d2
