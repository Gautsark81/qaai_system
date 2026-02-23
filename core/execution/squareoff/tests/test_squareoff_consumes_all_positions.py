from core.execution.squareoff.consumer import SquareOffConsumer
from core.execution.squareoff.intent import SquareOffIntent
from core.execution.execution_intent import ExecutionIntent


def test_squareoff_consumes_all_positions():
    positions = {
        "RELIANCE": 100,
        "INFY": -50,
    }

    intent = SquareOffIntent(
        reason="Market close",
        audit_id="AUDIT-001",
    )

    consumer = SquareOffConsumer(
        positions=positions,
        squareoff_intent=intent,
    )

    exec_intents = consumer.consume()

    assert len(exec_intents) == 2
    symbols = {i.symbol for i in exec_intents}
    assert symbols == {"RELIANCE", "INFY"}

    for i in exec_intents:
        assert isinstance(i, ExecutionIntent)
        assert i.reason == "Market close"
        assert i.audit_id == "AUDIT-001"
