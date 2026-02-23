from core.dashboard_read.replay.engine import OfflineReplayEngine


def test_replay_engine_produces_deterministic_id(deterministic_replay):
    snapshot = deterministic_replay
    engine = OfflineReplayEngine()

    result1 = engine.replay(snapshot)
    result2 = engine.replay(snapshot)

    assert result1.replay_id == result2.replay_id
    assert result1.snapshot_hash == snapshot.snapshot.snapshot_hash
    assert result1.chain_hash == snapshot.snapshot.chain_hash


def test_replay_engine_replays_all_components(deterministic_replay):
    snapshot = deterministic_replay
    engine = OfflineReplayEngine()

    result = engine.replay(snapshot)

    assert set(result.replayed_components) == set(
        snapshot.snapshot.components.keys()
    )
    assert result.is_clean is True


def test_replay_engine_detects_integrity_failure(deterministic_replay, monkeypatch):
    snapshot = deterministic_replay
    engine = OfflineReplayEngine()

    monkeypatch.setattr(
        "core.dashboard_read.replay.engine._verify_snapshot",
        lambda _: type("R", (), {"is_valid": False})(),
    )

    result = engine.replay(snapshot)

    assert result.verification_status is False
    assert result.discrepancies