from core.reproducibility.environment_snapshot import (
    EnvironmentSnapshotBuilder,
)
from core.reproducibility.environment_hash import EnvironmentHasher


def test_environment_hash_is_deterministic():
    builder = EnvironmentSnapshotBuilder()
    snapshot = builder.build()

    h1 = EnvironmentHasher.hash(snapshot)
    h2 = EnvironmentHasher.hash(snapshot)

    assert h1 == h2