import inspect
from datetime import datetime

from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_decision import RetryDecision
from core.execution.broker_response.governance.retry_builder import (
    build_retry_recommendation,
)


# ---------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------
def _accepted_response():
    return BrokerResponse(
        broker="PAPER",
        order_id="ORD-1",
        status="FILLED",
        filled_quantity=10,
        avg_price=100.0,
        timestamp=datetime.utcnow(),
    )


def _transient_failure_response():
    return BrokerResponse(
        broker="PAPER",
        order_id="ORD-2",
        status="REJECTED",
        filled_quantity=0,
        avg_price=0.0,
        rejection_reason="temporary network issue",
        timestamp=datetime.utcnow(),
    )


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------
def test_builder_is_deterministic_for_same_response():
    response = _accepted_response()

    r1 = build_retry_recommendation(response)
    r2 = build_retry_recommendation(response)

    assert r1 == r2
    assert r1.response_hash == response.response_hash


def test_successful_execution_is_non_retryable():
    response = _accepted_response()

    recommendation = build_retry_recommendation(response)

    assert recommendation.outcome == BrokerOutcome.SUCCESS
    assert recommendation.retry_decision == RetryDecision.NON_RETRYABLE


def test_transient_failure_is_retryable():
    response = _transient_failure_response()

    recommendation = build_retry_recommendation(response)

    assert recommendation.retry_decision == RetryDecision.RETRYABLE


def test_builder_does_not_mutate_response():
    response = _accepted_response()
    before = response.response_hash

    _ = build_retry_recommendation(response)

    after = response.response_hash
    assert before == after


def test_builder_has_no_execution_authority():
    source = inspect.getsource(build_retry_recommendation).lower()

    forbidden = [
        "execute",
        "retry(",
        "sleep",
        "call(",
        "broker",
    ]

    for word in forbidden:
        assert word not in source
