from core.execution.engine import ExecutionEngine
from core.telemetry.testing import InMemoryTelemetrySink


def test_execution_telemetry_emitted_only_once_per_run():
    """
    Invariant:
    - execute() may be retried
    - telemetry must emit at most once per run
    """

    sink = InMemoryTelemetrySink()
    engine = ExecutionEngine(telemetry_sink=sink)

    engine.execute(
        run_id="RUN-1",
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    assert len(sink.events) == 1

    # Retry with same run_id
    engine.execute(
        run_id="RUN-1",
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    # 🔒 MUST remain one
    assert len(sink.events) == 1
