import inspect

from core.operator_reality.intent import OperatorIntentFactory
from core.operator_reality.acknowledgment import OperatorAcknowledgmentService
from core.operator_reality.models import OperatorIntent, OperatorAcknowledgment


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

def _sample_intent() -> OperatorIntent:
    return OperatorIntentFactory.create(
        operator_id="operator-001",
        intent_type="ENABLE_LIVE",
        scope="system",
        timestamp=1700000000,
        note="initial live enable",
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_operator_intent_is_created_and_immutable():
    intent = _sample_intent()

    assert isinstance(intent, OperatorIntent)
    assert intent.operator_id == "operator-001"
    assert intent.intent_type == "ENABLE_LIVE"
    assert intent.scope == "system"
    assert intent.timestamp == 1700000000


def test_acknowledgment_is_created():
    intent = _sample_intent()

    ack = OperatorAcknowledgmentService.acknowledge(
        intent=intent,
        evidence_id="evidence-123",
    )

    assert isinstance(ack, OperatorAcknowledgment)
    assert ack.acknowledged is True
    assert ack.intent == intent
    assert ack.evidence_id == "evidence-123"


def test_acknowledgment_is_deterministic():
    intent = _sample_intent()

    a1 = OperatorAcknowledgmentService.acknowledge(
        intent=intent,
        evidence_id="evidence-xyz",
    )
    a2 = OperatorAcknowledgmentService.acknowledge(
        intent=intent,
        evidence_id="evidence-xyz",
    )

    assert a1 == a2


def test_acknowledgment_does_not_mutate_intent():
    intent = _sample_intent()
    before = intent

    _ = OperatorAcknowledgmentService.acknowledge(
        intent=intent,
        evidence_id="evidence-456",
    )

    assert intent == before


def test_no_execution_authority_present():
    source = inspect.getsource(OperatorAcknowledgmentService).lower()

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for word in forbidden:
        assert word not in source
