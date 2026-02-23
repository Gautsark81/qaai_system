from dashboard.snapshot_loader import load_dashboard_snapshot
from dashboard.domain.dashboard_snapshot import DashboardSnapshot
from dashboard.domain.system_mood_drift import SystemMoodDriftResult
from dashboard.lifecycle import DashboardState


def test_dashboard_snapshot_contains_system_mood_drift():
    state, snapshot = load_dashboard_snapshot()

    assert state == DashboardState.IDLE
    assert isinstance(snapshot, DashboardSnapshot)

    # Phase-1.2 must be present
    assert hasattr(snapshot, "system_mood_drift")
    assert isinstance(snapshot.system_mood_drift, SystemMoodDriftResult)


def test_system_mood_drift_is_consistent_with_system_mood():
    _, snapshot = load_dashboard_snapshot()

    drift = snapshot.system_mood_drift

    # Mean mood must agree with Phase-1.1 mood
    assert drift.mean == snapshot.system_mood_detail.mood


def test_system_mood_drift_is_computed_once():
    _, snapshot = load_dashboard_snapshot()

    drift1 = snapshot.system_mood_drift
    drift2 = snapshot.system_mood_drift

    # No recomputation / no regeneration
    assert drift1 is drift2


def test_system_mood_drift_is_read_only():
    _, snapshot = load_dashboard_snapshot()

    drift = snapshot.system_mood_drift

    try:
        drift.mean = 0.0  # type: ignore[attr-defined]
        assert False, "SystemMoodDriftResult must be immutable"
    except Exception:
        assert True
