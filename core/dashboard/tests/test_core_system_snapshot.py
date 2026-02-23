from dataclasses import FrozenInstanceError
from datetime import datetime
import pytest


def test_core_snapshot_is_constructible():
    """
    Snapshot must be constructible from finalized core components only.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    snapshot = CoreSystemSnapshot(
        timestamp=datetime(2026, 1, 18, 12, 0, 0),
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    assert snapshot.system_health == "HEALTHY"


def test_core_snapshot_is_fully_immutable():
    """
    Snapshot must be frozen and mutation-proof.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    snapshot = CoreSystemSnapshot(
        timestamp=datetime.utcnow(),
        system_health="DEGRADING",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.system_health = "UNSTABLE"


def test_snapshot_has_no_callables():
    """
    Snapshot must contain no executable logic.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    snapshot = CoreSystemSnapshot(
        timestamp=datetime.utcnow(),
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    for value in snapshot.__dict__.values():
        assert not callable(value)


def test_snapshot_is_deterministic():
    """
    Two snapshots built from identical inputs must be equal.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    ts = datetime(2026, 1, 18, 12, 0, 0)

    s1 = CoreSystemSnapshot(
        timestamp=ts,
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    s2 = CoreSystemSnapshot(
        timestamp=ts,
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    assert s1 == s2


def test_snapshot_contains_no_external_dependencies():
    """
    Snapshot must not depend on IO, DBs, or services.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    snapshot = CoreSystemSnapshot(
        timestamp=datetime.utcnow(),
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=(),
    )

    forbidden = ("db", "client", "broker", "redis", "api")

    for value in snapshot.__dict__.values():
        if isinstance(value, str):
            for f in forbidden:
                assert f not in value.lower()


def test_snapshot_alerts_are_tuple_and_immutable():
    """
    Alerts must be immutable and order-stable.
    """
    from core.dashboard.snapshot import CoreSystemSnapshot

    snapshot = CoreSystemSnapshot(
        timestamp=datetime.utcnow(),
        system_health="HEALTHY",
        screening=None,
        watchlist=None,
        strategies=None,
        capital=None,
        alerts=("ALERT_1", "ALERT_2"),
    )

    assert isinstance(snapshot.alerts, tuple)

    with pytest.raises(Exception):
        snapshot.alerts += ("ALERT_3",)
