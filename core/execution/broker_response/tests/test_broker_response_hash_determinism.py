from core.execution.broker_response.contracts import BrokerResponseContract, BrokerDecision
from core.execution.broker_response.models import broker_response_hash


def test_broker_response_hash_is_deterministic():
    r1 = BrokerResponseContract(
        execution_id="1",
        broker="PAPER",
        decision=BrokerDecision.ACCEPTED,
    )

    r2 = BrokerResponseContract(
        execution_id="1",
        broker="PAPER",
        decision=BrokerDecision.ACCEPTED,
    )

    assert broker_response_hash(r1) == broker_response_hash(r2)
