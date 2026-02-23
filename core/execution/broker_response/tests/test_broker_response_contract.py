from core.execution.broker_response.contracts import (
    BrokerResponseContract,
    BrokerDecision,
)


def test_broker_response_is_immutable():
    response = BrokerResponseContract(
        execution_id="exec-1",
        broker="PAPER",
        decision=BrokerDecision.ACCEPTED,
    )

    try:
        response.broker = "REAL"
        assert False
    except Exception:
        assert True
