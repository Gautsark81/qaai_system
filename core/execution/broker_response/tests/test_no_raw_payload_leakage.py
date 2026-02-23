from dataclasses import asdict

from core.execution.broker_response.adapters.paper import PaperBrokerAdapter


def test_adapter_does_not_leak_raw_broker_payload():
    adapter = PaperBrokerAdapter()

    raw_payload = {
        "quantity": 1,
        "price": 999.99,
        "internal_debug": {"foo": "bar"},
    }

    response = adapter.normalize(raw_payload)
    response_dict = asdict(response)

    # Raw payload must NEVER appear inside canonical response
    assert "raw" not in response_dict
    assert "payload" not in response_dict
    assert "internal_debug" not in str(response_dict)
