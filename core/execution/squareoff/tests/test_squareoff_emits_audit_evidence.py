from core.execution.squareoff.consumer import SquareOffConsumer
from core.execution.squareoff.intent import SquareOffIntent


def test_squareoff_emits_audit_evidence():
    intent = SquareOffIntent(
        reason="Risk breach",
        audit_id="AUDIT-004",
    )

    consumer = SquareOffConsumer(
        positions={"HDFCBANK": -15},
        squareoff_intent=intent,
    )

    consumer.consume()
    evidence = consumer.evidence

    assert evidence is not None
    assert evidence.audit_id == "AUDIT-004"
    assert evidence.reason == "Risk breach"
    assert "HDFCBANK" in evidence.positions
