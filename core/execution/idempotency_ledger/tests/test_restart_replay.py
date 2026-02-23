from datetime import datetime

from core.execution.idempotency_ledger import (
    ExecutionIdempotencyLedger,
    ExecutionIdempotencyRecord,
    IdempotencyDecision,
)


def test_replay_reconstructs_state():
    record = ExecutionIdempotencyRecord(
        execution_intent_id="E2",
        strategy_id="S2",
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        price=2500.0,
        timestamp=datetime.utcnow(),
    )

    ledger = ExecutionIdempotencyLedger()
    ledger.record(record)

    snapshot = ledger.entries()

    replayed = ExecutionIdempotencyLedger.replay(snapshot)

    result = replayed.record(record)
    assert result.decision == IdempotencyDecision.DUPLICATE
