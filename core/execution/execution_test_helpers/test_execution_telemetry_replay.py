from core.execution.engine import ExecutionEngine


class _TestTelemetrySink:
    """
    Local test sink implementing the real telemetry interface.
    No production dependency.
    """

    def __init__(self):
        self._events = []

    def emit_execution(self, event):
        self._events.append(event)

    def event_count(self) -> int:
        return len(self._events)


def test_execution_replay_does_not_emit_telemetry():
    """
    INVARIANT:
    Execution replay must be strictly read-only.
    Telemetry must be emitted at most once per run.
    """

    telemetry = _TestTelemetrySink()

    engine = ExecutionEngine(
        mode="paper",
        telemetry_sink=telemetry,
    )

    execution_request = {
        "strategy_id": "STRAT-1",
        "symbol": "NIFTY",
        "side": "BUY",
        "qty": 1,
    }

    # --- First execution ---
    engine.execute(execution_request)
    assert telemetry.event_count() == 1

    # --- Replay ---
    engine.replay(run_id=engine.run_id)

    # --- Invariant ---
    assert telemetry.event_count() == 1
