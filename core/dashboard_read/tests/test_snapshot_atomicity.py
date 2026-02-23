# core/dashboard_read/tests/test_snapshot_atomicity.py

import pytest
from core.dashboard_read.builder import SystemSnapshotBuilder, SnapshotBuildError


def test_snapshot_fails_atomically(monkeypatch):
    from core.dashboard_read import providers

    def boom():
        raise RuntimeError("provider failure")

    monkeypatch.setattr(
        providers.system_health,
        "build_system_health",
        boom,
    )

    builder = SystemSnapshotBuilder(
        execution_mode="offline",
        market_status="closed",
        system_version="test",
    )

    with pytest.raises(SnapshotBuildError):
        builder.build()
