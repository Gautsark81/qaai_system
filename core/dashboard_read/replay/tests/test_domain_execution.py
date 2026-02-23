from core.dashboard_read.replay.domains.execution import replay_execution


def test_replay_execution_structure(deterministic_replay):
    snapshot = deterministic_replay.snapshot

    result = replay_execution(snapshot)

    assert "orders" in result
    assert "count" in result
    assert "raw" in result

    assert isinstance(result["orders"], list)
    assert isinstance(result["count"], int)