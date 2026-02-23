from datetime import datetime

from core.execution.idempotency_ledger import (
    ExecutionIdempotencyLedger,
    ExecutionIdempotencyRecord,
    IdempotencyDecision,
)


def test_duplicate_execution_is_blocked():
    ledger = ExecutionIdempotencyLedger()

    record = ExecutionIdempotencyRecord(
        execution_intent_id="E1",
        strategy_id="S1",
        symbol="BANKNIFTY",
        side="SELL",
        quantity=5,
        price=200.0,
        timestamp=datetime.utcnow(),
    )

    first = ledger.record(record)
    second = ledger.record(record)

    assert first.decision == IdempotencyDecision.ACCEPTED
    assert second.decision == IdempotencyDecision.DUPLICATE
