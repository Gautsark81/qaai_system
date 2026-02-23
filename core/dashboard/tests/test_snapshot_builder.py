from datetime import datetime
import pytest


class DummyScreening:
    total = 100
    passed = 60
    failed = 40
    blocked_symbols = ("XYZ",)


class DummyWatchlist:
    active = ("TCS", "INFY")
    suspended = ("ABC",)
    retired = ()


class DummyStrategyIntel:
    healthy = ("S1", "S2")
    degrading = ("S3",)
    unstable = ()


class DummyCapital:
    total = 1_000_000.0
    allocated = 600_000.0
    free = 400_000.0
    per_strategy = {"S1": 300_000.0, "S2": 300_000.0}


def test_snapshot_builder_constructs_snapshot():
    """
    Builder must produce a CoreSystemSnapshot from finalized core components.
    """
    from core.dashboard.builder import SnapshotBuilder
    from core.dashboard.snapshot import CoreSystemSnapshot

    builder = SnapshotBuilder(
        screening=DummyScreening(),
        watchlist=DummyWatchlist(),
        strategies=DummyStrategyIntel(),
        capital=DummyCapital(),
    )

    snapshot = builder.build(timestamp=datetime(2026, 1, 18, 12, 30))

    assert isinstance(snapshot, CoreSystemSnapshot)
    assert snapshot.watchlist.active == ("TCS", "INFY")
    assert snapshot.capital.free == 400_000.0


def test_snapshot_builder_is_deterministic():
    """
    Same inputs must always produce identical snapshots.
    """
    from core.dashboard.builder import SnapshotBuilder

    builder = SnapshotBuilder(
        screening=DummyScreening(),
        watchlist=DummyWatchlist(),
        strategies=DummyStrategyIntel(),
        capital=DummyCapital(),
    )

    ts = datetime(2026, 1, 18, 12, 30)

    s1 = builder.build(timestamp=ts)
    s2 = builder.build(timestamp=ts)

    assert s1 == s2


def test_snapshot_builder_has_no_side_effects():
    """
    Builder must not mutate inputs or perform IO.
    """
    from core.dashboard.builder import SnapshotBuilder

    screening = DummyScreening()
    watchlist = DummyWatchlist()

    builder = SnapshotBuilder(
        screening=screening,
        watchlist=watchlist,
        strategies=DummyStrategyIntel(),
        capital=DummyCapital(),
    )

    builder.build(timestamp=datetime.utcnow())

    # Inputs unchanged
    assert screening.total == 100
    assert watchlist.active == ("TCS", "INFY")


def test_snapshot_builder_rejects_missing_components():
    """
    All components are mandatory.
    """
    from core.dashboard.builder import SnapshotBuilder

    with pytest.raises(TypeError):
        SnapshotBuilder(
            screening=None,
            watchlist=None,
            strategies=None,
            capital=None,
        )
