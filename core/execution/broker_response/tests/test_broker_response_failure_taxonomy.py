from core.execution.broker_response.contracts import BrokerDecision


def test_failure_taxonomy_is_explicit():
    assert BrokerDecision.REJECTED.value == "REJECTED"
    assert BrokerDecision.TRANSIENT_FAILURE.value == "TRANSIENT_FAILURE"
    assert BrokerDecision.UNKNOWN_STATE.value == "UNKNOWN_STATE"
