# core/dashboard_read/tests/test_snapshot_build.py

from core.dashboard_read.builder import SystemSnapshotBuilder
from core.dashboard_read.snapshot import SystemSnapshot


def test_snapshot_build_success():
    builder = SystemSnapshotBuilder(
        execution_mode="offline",
        market_status="closed",
        system_version="test",
    )

    snapshot = builder.build()

    assert isinstance(snapshot, SystemSnapshot)
    assert snapshot.meta.execution_mode == "offline"
    assert snapshot.meta.market_status == "closed"
    assert snapshot.meta.system_version == "test"
