from datetime import datetime

from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.classifier import ResponseClassifier


def test_classifier_is_deterministic():
    response = BrokerResponse(
        decision="REJECTED",
        filled_quantity=0,
        average_price=0.0,
        broker_reference="PAPER",
        order_id="DET-1",
        rejection_reason="temporary network failure",
        timestamp=datetime.utcnow(),
    )

    o1 = ResponseClassifier.classify(response)
    o2 = ResponseClassifier.classify(response)

    assert o1 == o2
