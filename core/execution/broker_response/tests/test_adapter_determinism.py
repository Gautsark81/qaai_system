from core.execution.broker_response.adapters.paper import PaperBrokerAdapter


def test_adapter_is_deterministic_for_same_input():
    adapter = PaperBrokerAdapter()

    raw_payload = {
        "quantity": 5,
        "price": 1200.0,
        "order_id": "PAPER-XYZ",
    }

    r1 = adapter.normalize(raw_payload)
    r2 = adapter.normalize(raw_payload)

    assert r1 == r2
    assert hash(r1) == hash(r2)
