import pytest

from core.dashboard_read.builder import SystemSnapshotBuilder
from core.dashboard_read.snapshot import SystemSnapshot


def test_snapshot_builder_never_crashes(monkeypatch):
    """
    D-3 GUARANTEE:
    Snapshot build must never crash even if providers explode.
    """

    def explode():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "core.dashboard_read.providers.market_state.build_market_state",
        explode,
    )

    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="test",
    )

    snapshot = builder.build()

    assert isinstance(snapshot, SystemSnapshot)
