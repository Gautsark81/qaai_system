def test_execution_restart_replay():
    ledger = ExecutionIdempotencyLedger()

    engine1 = ExecutionEngine(
        broker_executor=lambda _: None,
        idempotency_ledger=ledger,
    )

    intent = ExecutionIntent.example()

    engine1.execute(intent)

    # simulate restart
    engine2 = ExecutionEngine(
        broker_executor=lambda _: None,
        idempotency_ledger=ledger,
    )

    result = engine2.execute(intent)

    assert result.idempotency_decision == "DUPLICATE"
