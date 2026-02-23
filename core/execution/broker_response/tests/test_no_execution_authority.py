from core.execution.broker_response.contracts import BrokerResponseContract


def test_broker_response_has_no_execution_methods():
    response = BrokerResponseContract(
        execution_id="x",
        broker="PAPER",
        decision="ACCEPTED",
    )

    forbidden = {"execute", "retry", "submit", "cancel"}

    for name in forbidden:
        assert not hasattr(response, name)
