from dashboard.snapshot_loader import load_dashboard_snapshot
from dashboard.domain.dashboard_snapshot import DashboardSnapshot
from dashboard.domain.system_mood import SystemMoodResult
from dashboard.lifecycle import DashboardState


def test_dashboard_snapshot_wraps_core_snapshot_and_mood():
    state, snapshot = load_dashboard_snapshot()

    assert state == DashboardState.IDLE
    assert isinstance(snapshot, DashboardSnapshot)

    # Core snapshot preserved
    assert snapshot.core is not None

    # Phase-1.1 explainability attached
    assert isinstance(snapshot.system_mood_detail, SystemMoodResult)

    # Numeric mood must agree
    assert snapshot.system_mood_detail.mood == snapshot.system_mood


def test_dashboard_snapshot_is_read_only_and_deterministic():
    _, snapshot1 = load_dashboard_snapshot()
    _, snapshot2 = load_dashboard_snapshot()

    # Independent loads, same values
    assert snapshot1.system_mood_detail.mood == snapshot2.system_mood_detail.mood

    # No recomputation via access
    assert snapshot1.system_mood_detail is snapshot1.system_mood_detail
