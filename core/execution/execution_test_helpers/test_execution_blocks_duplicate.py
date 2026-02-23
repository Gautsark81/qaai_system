def test_execution_blocks_duplicate():
    engine = ExecutionEngine(
        broker_executor=lambda _: (_ for _ in ()).throw(RuntimeError("should not call")),
        idempotency_ledger=ExecutionIdempotencyLedger(),
    )

    intent = ExecutionIntent.example()

    engine.execute(intent)
    result = engine.execute(intent)

    assert result.idempotency_decision == "DUPLICATE"
