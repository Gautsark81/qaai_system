def test_execution_no_broker_call_on_duplicate():
    called = False

    def broker(_):
        nonlocal called
        called = True

    engine = ExecutionEngine(
        broker_executor=broker,
        idempotency_ledger=ExecutionIdempotencyLedger(),
    )

    intent = ExecutionIntent.example()

    engine.execute(intent)
    engine.execute(intent)

    assert called is True  # first only
