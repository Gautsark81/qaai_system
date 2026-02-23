def test_execution_allows_first_only():
    calls = []

    def broker(intent):
        calls.append(intent.execution_id)

    engine = ExecutionEngine(
        broker_executor=broker,
        idempotency_ledger=ExecutionIdempotencyLedger(),
    )

    intent = ExecutionIntent.example()

    r1 = engine.execute(intent)
    r2 = engine.execute(intent)

    assert r1.status == "SUCCESS"
    assert r2.status == "BLOCKED"
    assert len(calls) == 1
