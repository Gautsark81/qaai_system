from datetime import datetime

from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.classifier import ResponseClassifier


def test_successful_fill_classifies_as_success():
    response = BrokerResponse(
        decision="ACCEPTED",
        filled_quantity=10,
        average_price=100.0,
        broker_reference="PAPER",
        order_id="X1",
        timestamp=datetime.utcnow(),
    )

    outcome = ResponseClassifier.classify(response)
    assert outcome == BrokerOutcome.SUCCESS


def test_rejected_zero_fill_classifies_as_rejected():
    response = BrokerResponse(
        decision="ACCEPTED",
        filled_quantity=0,
        average_price=0.0,
        broker_reference="PAPER",
        order_id="X2",
        timestamp=datetime.utcnow(),
    )

    outcome = ResponseClassifier.classify(response)
    assert outcome == BrokerOutcome.REJECTED
