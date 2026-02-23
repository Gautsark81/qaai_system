from unittest.mock import Mock
from core.execution.squareoff.consumer import SquareOffConsumer
from core.execution.squareoff.intent import SquareOffIntent


def test_squareoff_does_not_touch_strategy():
    strategy = Mock()

    intent = SquareOffIntent(
        reason="Market close",
        audit_id="AUDIT-005",
    )

    consumer = SquareOffConsumer(
        positions={"ITC": 30},
        squareoff_intent=intent,
        strategy=strategy,
    )

    consumer.consume()

    strategy.assert_not_called()
