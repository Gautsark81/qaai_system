from core.dashboard_read.providers.capital import build_capital_state
from core.dashboard_read.snapshot import CapitalState


def test_capital_state(monkeypatch):
    class DummyCapitalMetrics:
        total_capital = 1_000_000.0
        allocated_capital = 600_000.0
        free_capital = 400_000.0
        utilization_ratio = 0.6
        throttle_active = False

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.capital.read_capital_metrics",
        lambda: DummyCapitalMetrics(),
    )

    state = build_capital_state()

    assert isinstance(state, CapitalState)
    assert state.free_capital == 400_000.0
    assert state.utilization_ratio == 0.6
    assert state.throttle_active is False
