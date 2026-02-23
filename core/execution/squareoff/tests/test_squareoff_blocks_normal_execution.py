import pytest
from core.execution.squareoff.consumer import SquareOffConsumer
from core.execution.squareoff.intent import SquareOffIntent


def test_squareoff_blocks_normal_execution():
    intent = SquareOffIntent(
        reason="Kill switch",
        audit_id="AUDIT-002",
    )

    consumer = SquareOffConsumer(
        positions={"TCS": 10},
        squareoff_intent=intent,
    )

    with pytest.raises(RuntimeError):
        consumer.assert_normal_execution_allowed()
