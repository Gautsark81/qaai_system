from core.dashboard_read.providers.incidents import build_incident_state
from core.dashboard_read.snapshot import IncidentState


def test_incident_state(monkeypatch):
    class DummyIncidentMetrics:
        open_incidents = 1
        total_incidents = 5
        last_incident_type = "CAPITAL_FREEZE"
        capital_frozen = True

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.incidents.read_incident_metrics",
        lambda: DummyIncidentMetrics(),
    )

    state = build_incident_state()

    assert isinstance(state, IncidentState)
    assert state.open_incidents == 1
    assert state.capital_frozen is True
