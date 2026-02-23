from datetime import datetime

from core.execution.idempotency_ledger.models import ExecutionIdempotencyRecord


def test_identity_hash_is_deterministic():
    ts = datetime.utcnow()

    r1 = ExecutionIdempotencyRecord(
        execution_intent_id="E3",
        strategy_id="S3",
        symbol="INFY",
        side="BUY",
        quantity=15,
        price=1500.0,
        timestamp=ts,
    )

    r2 = ExecutionIdempotencyRecord(
        execution_intent_id="E3",
        strategy_id="S3",
        symbol="INFY",
        side="BUY",
        quantity=15,
        price=1500.0,
        timestamp=ts,
    )

    assert r1.identity_hash() == r2.identity_hash()
