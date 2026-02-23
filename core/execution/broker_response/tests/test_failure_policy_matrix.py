from core.execution.broker_response.contracts import BrokerDecision
from core.execution.broker_response.policy import policy_for


def test_failure_policy_matrix():
    p = policy_for(BrokerDecision.ACCEPTED)
    assert not p.retry_allowed
    assert not p.escalate
    assert p.replay_safe

    p = policy_for(BrokerDecision.TRANSIENT_FAILURE)
    assert p.retry_allowed
    assert not p.escalate
    assert not p.replay_safe
