from core.dashboard_read.replay_viewer.viewer import render_replay_view
from core.dashboard_read.replay.report import build_replay_report


def test_replay_viewer_is_read_only(deterministic_replay):
    snapshot = deterministic_replay.snapshot
    report = build_replay_report(snapshot)

    view = render_replay_view(snapshot, report)

    assert "integrity" in view
    assert "coverage" in view
    assert "snapshot" in view
    assert "replay" in view

    # Viewer must not mutate snapshot
    assert snapshot.snapshot_hash == view["integrity"]["snapshot_hash"]