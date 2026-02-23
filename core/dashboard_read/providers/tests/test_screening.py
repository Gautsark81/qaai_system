from core.dashboard_read.providers.screening import build_screening_state
from core.dashboard_read.snapshot import ScreeningState


def test_screening(monkeypatch):
    class DummyMetrics:
        symbols_seen = 10
        passed = 4
        rejected_by_reason = {"volatility": 6}

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.screening.read_screening_metrics",
        lambda: DummyMetrics(),
    )

    state = build_screening_state()

    assert isinstance(state, ScreeningState)
    assert state.passed == 4
