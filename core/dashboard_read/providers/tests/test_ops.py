from core.dashboard_read.providers.ops import build_ops_state
from core.dashboard_read.snapshot import OpsState


def test_ops_state(monkeypatch):
    class DummyOpsMetrics:
        uptime_seconds = 86400
        restart_count = 1
        degraded_services = ["data_feed"]
        last_error = "TimeoutError"

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.ops.read_ops_metrics",
        lambda: DummyOpsMetrics(),
    )

    state = build_ops_state()

    assert isinstance(state, OpsState)
    assert state.human_control is False
