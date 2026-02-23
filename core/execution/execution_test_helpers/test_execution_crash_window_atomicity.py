from core.execution.engine import ExecutionEngine
from core.telemetry.testing import InMemoryTelemetrySink


def test_execution_crash_between_commit_and_retry_is_safe():
    sink = InMemoryTelemetrySink()

    engine = ExecutionEngine(telemetry_sink=sink)

    # First execution
    engine.execute(
        run_id="RUN-CRASH-1",
        strategy_id="S1",
        symbol="BANKNIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    assert len(sink.events()) == 1

    # Simulate crash by recreating engine (process restart)
    engine = ExecutionEngine(telemetry_sink=sink)

    # Retry same run_id
    engine.execute(
        run_id="RUN-CRASH-1",
        strategy_id="S1",
        symbol="BANKNIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    # ❗ Must NOT emit again
    assert len(sink.events()) == 1
