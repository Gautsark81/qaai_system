from core.dashboard_read.providers.execution import build_execution_state
from core.dashboard_read.snapshot import ExecutionState


def test_execution_state(monkeypatch):
    class DummyPosition:
        symbol = "NIFTY"
        quantity = 50
        exposure = 100000.0
        stop_loss = 19500.0

    class DummyMetrics:
        intents_created = 10
        intents_blocked = 2
        blocked_reasons = {"risk": 2}
        positions = [DummyPosition()]
        fills = 5

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.execution.read_execution_metrics",
        lambda: DummyMetrics(),
    )

    state = build_execution_state()

    assert isinstance(state, ExecutionState)
    assert state.intents_created == 10
    assert state.positions[0].symbol == "NIFTY"
