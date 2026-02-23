from core.dashboard_read.builder import SystemSnapshotBuilder


def test_snapshot_fingerprint_is_deterministic():
    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="v1",
    )

    s1 = builder.build()
    s2 = builder.build()

    assert s1.meta.fingerprint == s2.meta.fingerprint


def test_snapshot_fingerprint_changes_on_state_change(monkeypatch):
    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="v1",
    )

    s1 = builder.build()

    # Force a controlled degradation
    monkeypatch.setattr(
        "core.dashboard_read.providers.market_state.build_market_state",
        lambda: (_ for _ in ()).throw(RuntimeError("market down")),
    )

    s2 = builder.build()

    assert s1.meta.fingerprint != s2.meta.fingerprint


def test_snapshot_fingerprint_ignores_snapshot_id_and_time():
    builder = SystemSnapshotBuilder(
        execution_mode="offline",
        market_status="closed",
        system_version="v1",
    )

    s1 = builder.build()
    s2 = builder.build()

    assert s1.meta.snapshot_id != s2.meta.snapshot_id
    assert s1.meta.created_at != s2.meta.created_at

    # Fingerprint must still match
    assert s1.meta.fingerprint == s2.meta.fingerprint
