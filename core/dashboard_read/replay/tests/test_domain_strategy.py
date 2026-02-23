from core.dashboard_read.replay.domains.strategy import replay_strategy


def test_replay_strategy_structure(deterministic_replay):
    snapshot = deterministic_replay.snapshot

    result = replay_strategy(snapshot)

    assert "count" in result
    assert "strategies" in result
    assert "raw" in result

    assert isinstance(result["count"], int)
    assert isinstance(result["strategies"], list)
    assert isinstance(result["raw"], dict)