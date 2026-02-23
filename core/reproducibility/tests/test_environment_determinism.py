from core.reproducibility.environment_snapshot import (
    EnvironmentSnapshot,
)
from core.reproducibility.environment_hash import EnvironmentHasher


def test_manual_snapshot_hash_stable():
    snapshot = EnvironmentSnapshot(
        python_version="3.11",
        platform_system="Windows",
        platform_release="10",
        machine="x86_64",
        processor="Intel",
        timezone="Asia/Kolkata",
        installed_packages=["a", "b", "c"],
    )

    h1 = EnvironmentHasher.hash(snapshot)
    h2 = EnvironmentHasher.hash(snapshot)

    assert h1 == h2