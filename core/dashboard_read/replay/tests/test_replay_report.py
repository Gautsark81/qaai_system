from core.dashboard_read.replay.report import build_replay_report


def test_build_full_replay_report(deterministic_replay):
    snapshot = deterministic_replay.snapshot

    report = build_replay_report(snapshot)

    assert report.strategy is not None
    assert report.risk is not None
    assert report.capital is not None
    assert report.execution is not None
    assert report.compliance is not None

    assert isinstance(report.is_consistent, bool)