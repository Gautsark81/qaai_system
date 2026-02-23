# core/execution/tests/test_execution_telemetry_ordering.py

from core.execution.engine import ExecutionEngine
from core.telemetry.testing import InMemoryTelemetrySink


def test_execution_telemetry_is_strictly_monotonic():
    sink = InMemoryTelemetrySink()
    engine = ExecutionEngine(telemetry_sink=sink)

    engine.execute(
        intent_id="INTENT-1",
        symbol="AAPL",
        quantity=10,
        price=100.0,
        run_id="RUN-ORDER-1",
    )

    events = sink.events()
    assert len(events) >= 1

    seqs = [e.sequence for e in events]
    assert seqs == sorted(seqs), "Telemetry sequence must be monotonic"


def test_execution_replay_does_not_advance_sequence():
    sink = InMemoryTelemetrySink()
    engine = ExecutionEngine(telemetry_sink=sink)

    engine.execute(
        intent_id="INTENT-2",
        symbol="MSFT",
        quantity=5,
        price=200.0,
        run_id="RUN-ORDER-2",
    )

    before = sink.events()[-1].sequence

    # Replay (read-only)
    engine.execute(
        intent_id="INTENT-2",
        symbol="MSFT",
        quantity=5,
        price=200.0,
        run_id="RUN-ORDER-2",
        replay=True,
    )

    after = sink.events()[-1].sequence
    assert before == after


def test_execution_retry_does_not_reorder_sequence():
    sink = InMemoryTelemetrySink()
    engine = ExecutionEngine(telemetry_sink=sink)

    engine.execute(
        intent_id="INTENT-3",
        symbol="TSLA",
        quantity=1,
        price=300.0,
        run_id="RUN-ORDER-3",
    )

    engine.execute(
        intent_id="INTENT-3",
        symbol="TSLA",
        quantity=1,
        price=300.0,
        run_id="RUN-ORDER-3",
    )

    events = sink.events()
    seqs = [e.sequence for e in events]
    assert seqs == sorted(seqs)
