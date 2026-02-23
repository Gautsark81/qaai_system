from core.dashboard_read.providers.risk import build_risk_state
from core.dashboard_read.snapshot import RiskState


def test_risk_state(monkeypatch):
    class DummyRiskMetrics:
        checks_passed = 10
        checks_failed = 2
        dominant_violation = "POSITION_TOO_LARGE"
        freeze_active = False

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.risk.read_risk_metrics",
        lambda: DummyRiskMetrics(),
    )

    state = build_risk_state()

    assert isinstance(state, RiskState)
    assert state.checks_failed == 2
    assert state.dominant_violation == "POSITION_TOO_LARGE"
    assert state.freeze_active is False
