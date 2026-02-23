# core/dashboard_read/tests/test_snapshot_immutable.py

import pytest
from core.dashboard_read.builder import SystemSnapshotBuilder


def test_snapshot_is_immutable():
    builder = SystemSnapshotBuilder(
        execution_mode="offline",
        market_status="closed",
        system_version="test",
    )

    snapshot = builder.build()

    with pytest.raises(Exception):
        snapshot.meta.execution_mode = "live"
