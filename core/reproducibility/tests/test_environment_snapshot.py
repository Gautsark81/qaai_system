import pytest
from core.reproducibility.environment_snapshot import (
    EnvironmentSnapshotBuilder,
    EnvironmentSnapshot,
)


def test_snapshot_builds():
    builder = EnvironmentSnapshotBuilder()
    snapshot = builder.build()

    assert isinstance(snapshot, EnvironmentSnapshot)
    assert snapshot.timezone == "Asia/Kolkata"
    assert isinstance(snapshot.installed_packages, list)