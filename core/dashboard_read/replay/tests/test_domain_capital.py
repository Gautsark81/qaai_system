from core.dashboard_read.replay.domains.capital import replay_capital


def test_replay_capital_structure(deterministic_replay):
    snapshot = deterministic_replay.snapshot

    result = replay_capital(snapshot)

    assert "available" in result
    assert "used" in result
    assert "raw" in result