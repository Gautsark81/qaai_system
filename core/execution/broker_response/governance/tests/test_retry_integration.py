import inspect
from datetime import datetime

from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.retry_integration import (
    attach_retry_recommendation,
)
from core.execution.broker_response.governance.retry_recommendation import (
    RetryRecommendation,
)
from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_decision import RetryDecision


# ---------------------------------------------------------------------
# RETRY INTEGRATION — CONTRACT TESTS
# ---------------------------------------------------------------------


def _sample_response(
    *,
    filled_quantity: int = 10,
    avg_price: float = 100.0,
    status: str = "FILLED",
    rejection_reason: str | None = None,
):
    return BrokerResponse(
        broker="PAPER",
        order_id="ORD-123",
        status=status,
        filled_quantity=filled_quantity,
        avg_price=avg_price,
        timestamp=datetime.utcnow(),
        rejection_reason=rejection_reason,
    )


def test_retry_recommendation_is_attached():
    response = _sample_response()

    recommendation = attach_retry_recommendation(response)

    assert isinstance(recommendation, RetryRecommendation)


def test_retry_recommendation_is_deterministic_for_same_response():
    response = _sample_response()

    r1 = attach_retry_recommendation(response)
    r2 = attach_retry_recommendation(response)

    assert r1 == r2
    assert r1.recommendation_hash == r2.recommendation_hash


def test_retry_recommendation_does_not_mutate_response():
    response = _sample_response()
    before_hash = response.response_hash

    _ = attach_retry_recommendation(response)

    after_hash = response.response_hash
    assert before_hash == after_hash


def test_retry_recommendation_matches_outcome_mapping():
    response = _sample_response(filled_quantity=0, avg_price=0.0)

    recommendation = attach_retry_recommendation(response)

    assert recommendation.outcome in BrokerOutcome
    assert recommendation.retry_decision in RetryDecision


def test_retry_recommendation_is_replay_safe():
    response = _sample_response()

    r1 = attach_retry_recommendation(response)
    r2 = attach_retry_recommendation(response)

    assert r1.recommendation_hash == r2.recommendation_hash


def test_retry_integration_has_no_execution_authority():
    source = inspect.getsource(attach_retry_recommendation).lower()

    forbidden = [
        "execute",
        "retry",
        "sleep",
        "call(",
        "broker(",
        "while",
        "for ",
    ]

    for word in forbidden:
        assert word not in source
