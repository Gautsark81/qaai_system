def test_execution_propagates_decision():
    engine = ExecutionEngine(
        broker_executor=lambda _: None,
        idempotency_ledger=ExecutionIdempotencyLedger(),
    )

    intent = ExecutionIntent.example()
    result = engine.execute(intent)

    assert result.idempotency_decision == "ACCEPTED"
    assert result.ledger_entry_hash
