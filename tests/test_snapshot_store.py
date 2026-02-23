# path: tests/test_snapshot_store.py

import os
import tempfile

from qaai_system.portfolio.snapshot_store import SnapshotStore
from qaai_system.portfolio.models import PortfolioSnapshot


def test_snapshot_store_append_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "snapshots.jsonl")
        store = SnapshotStore(path)

        snap1 = PortfolioSnapshot(
            timestamp=1.0,
            equity=1000.0,
            cash=1000.0,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            gross_exposure=0.0,
            net_exposure=0.0,
            num_open_positions=0,
            positions={},
        )
        snap2 = PortfolioSnapshot(
            timestamp=2.0,
            equity=1100.0,
            cash=900.0,
            realized_pnl=100.0,
            unrealized_pnl=0.0,
            gross_exposure=0.0,
            net_exposure=0.0,
            num_open_positions=0,
            positions={},
        )

        store.append_snapshot(snap1)
        store.append_snapshot(snap2)

        # Latest snapshot matches snap2
        latest = store.load_latest()
        assert latest is not None
        assert latest["timestamp"] == snap2.timestamp
        assert latest["equity"] == snap2.equity

        # load_last_n(1) returns only snap2
        last1 = store.load_last_n(1)
        assert len(last1) == 1
        assert last1[0]["timestamp"] == snap2.timestamp

        # load_last_n(2) returns [snap1, snap2] in order
        last2 = store.load_last_n(2)
        assert len(last2) == 2
        assert last2[0]["timestamp"] == snap1.timestamp
        assert last2[1]["timestamp"] == snap2.timestamp
