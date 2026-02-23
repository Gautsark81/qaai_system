from core.dashboard_read.replay.domains.risk import replay_risk


def test_replay_risk_structure(deterministic_replay):
    snapshot = deterministic_replay.snapshot

    result = replay_risk(snapshot)

    assert "blocks" in result
    assert "warnings" in result
    assert "raw" in result

    assert isinstance(result["blocks"], list)
    assert isinstance(result["warnings"], list)