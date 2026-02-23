from core.execution.broker_response.contracts import BrokerDecision
from core.execution.broker_response.policy import policy_for


def test_policy_is_deterministic():
    assert policy_for(BrokerDecision.REJECTED) == policy_for(BrokerDecision.REJECTED)
