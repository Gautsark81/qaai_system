# core/dashboard_read/tests/test_snapshot_meta.py

from core.dashboard_read.builder import SystemSnapshotBuilder


def test_snapshot_meta_fields():
    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="v1",
    )

    s1 = builder.build()
    s2 = builder.build()

    assert s1.meta.snapshot_id != s2.meta.snapshot_id
    assert s1.meta.created_at.tzinfo is not None
