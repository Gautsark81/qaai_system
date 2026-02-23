from datetime import datetime

from core.execution.idempotency_ledger import (
    ExecutionIdempotencyLedger,
    ExecutionIdempotencyRecord,
)


def test_ledger_is_append_only():
    ledger = ExecutionIdempotencyLedger()

    record = ExecutionIdempotencyRecord(
        execution_intent_id="E1",
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=10,
        price=100.0,
        timestamp=datetime.utcnow(),
    )

    ledger.record(record)

    entries = ledger.entries()
    assert len(entries) == 1

    try:
        entries.append(record)
    except Exception:
        pass

    assert len(ledger.entries()) == 1
