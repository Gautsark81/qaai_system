from core.execution.intent import ExecutionIntent


def test_execution_intent_is_venue_agnostic():
    paper_intent = ExecutionIntent(
        symbol="INFY",
        side="BUY",
        quantity=10,
        price=1500.0,
        venue="PAPER",
    )

    live_intent = ExecutionIntent(
        symbol="INFY",
        side="BUY",
        quantity=10,
        price=1500.0,
        venue="LIVE",
    )

    assert paper_intent.symbol == live_intent.symbol
    assert paper_intent.side == live_intent.side
    assert paper_intent.quantity == live_intent.quantity
    assert paper_intent.price == live_intent.price
