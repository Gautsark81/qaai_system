from core.execution.broker_response.adapters.paper import PaperBrokerAdapter
from core.execution.broker_response.contracts import BrokerDecision
from core.execution.broker_response.models import BrokerResponse


def test_adapter_normalizes_raw_payload_into_canonical_response():
    adapter = PaperBrokerAdapter()

    raw_payload = {
        "quantity": 10,
        "price": 2450.50,
        "order_id": "PAPER-123",
    }

    response = adapter.normalize(raw_payload)

    assert isinstance(response, BrokerResponse)
    assert response.decision == BrokerDecision.ACCEPTED
    assert response.filled_quantity == 10
    assert response.average_price == 2450.50
    assert response.broker_reference == "PAPER"
