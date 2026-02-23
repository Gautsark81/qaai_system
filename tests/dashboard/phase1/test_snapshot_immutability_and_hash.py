import pytest
from dataclasses import FrozenInstanceError

from dashboard.snapshot_loader import load_dashboard_snapshot
from dashboard.domain.dashboard_snapshot import DashboardSnapshot


def test_snapshot_has_hash():
    _, snapshot = load_dashboard_snapshot()

    assert hasattr(snapshot, "hash")
    assert hasattr(snapshot, "hash_algo")

    assert isinstance(snapshot.hash, str)
    assert isinstance(snapshot.hash_algo, str)


def test_snapshot_hash_is_deterministic():
    _, s1 = load_dashboard_snapshot()
    _, s2 = load_dashboard_snapshot()

    # Hash must be stable regardless of timestamp resolution
    assert s1.hash == s2.hash
    assert s1.hash_algo == s2.hash_algo


def test_snapshot_hash_changes_on_content_change():
    _, snapshot = load_dashboard_snapshot()
    original_hash = snapshot.hash

    mutated_core = dict(snapshot.core)
    mutated_core["system_mood"] = snapshot.core["system_mood"] - 1.0

    mutated_snapshot = DashboardSnapshot(
        core=mutated_core,
        system_mood_detail=snapshot.system_mood_detail,
        system_mood_drift=snapshot.system_mood_drift,
        violation_pulse=snapshot.violation_pulse,
    )

    assert mutated_snapshot.hash != original_hash


def test_snapshot_is_immutable():
    _, snapshot = load_dashboard_snapshot()

    # Frozen dataclass
    with pytest.raises(FrozenInstanceError):
        snapshot.hash = "tampered"

    # Frozen core mapping
    with pytest.raises(TypeError):
        snapshot.core["system_mood"] = 0.0

    # Frozen nested mapping
    with pytest.raises(TypeError):
        snapshot.core["capital"]["allocated"] = 999.0
