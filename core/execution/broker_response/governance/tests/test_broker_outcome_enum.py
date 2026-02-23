from core.execution.broker_response.governance.outcome import BrokerOutcome


def test_broker_outcome_enum_is_stable():
    assert BrokerOutcome.SUCCESS.value == "SUCCESS"
    assert BrokerOutcome.RETRYABLE_FAILURE.value == "RETRYABLE_FAILURE"
