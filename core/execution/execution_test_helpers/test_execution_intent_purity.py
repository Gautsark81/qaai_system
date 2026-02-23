from core.execution.intent import ExecutionIntent


def test_execution_intent_is_hashable_and_replayable():
    intent1 = ExecutionIntent(
        symbol="TCS",
        side="SELL",
        quantity=5,
        price=3200.0,
        venue="PAPER",
    )

    intent2 = ExecutionIntent(
        symbol="TCS",
        side="SELL",
        quantity=5,
        price=3200.0,
        venue="PAPER",
    )

    assert intent1 == intent2
    assert hash(intent1) == hash(intent2)
