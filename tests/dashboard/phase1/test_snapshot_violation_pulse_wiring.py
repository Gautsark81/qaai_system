from dashboard.snapshot_loader import load_dashboard_snapshot
from dashboard.domain.violation_pulse import ViolationPulseResult


def test_snapshot_contains_violation_pulse():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "violation_pulse")
    assert isinstance(snapshot.violation_pulse, ViolationPulseResult)


def test_violation_pulse_is_deterministic():
    _, s1 = load_dashboard_snapshot()
    _, s2 = load_dashboard_snapshot()

    assert s1.violation_pulse.score == s2.violation_pulse.score
