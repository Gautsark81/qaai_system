from core.reproducibility.environment_snapshot import (
    EnvironmentSnapshotBuilder,
)


def test_snapshot_has_no_execution_authority():
    builder = EnvironmentSnapshotBuilder()
    snapshot = builder.build()

    # Ensure it exposes no execution or capital mutation methods
    assert not hasattr(snapshot, "execute")
    assert not hasattr(snapshot, "allocate")