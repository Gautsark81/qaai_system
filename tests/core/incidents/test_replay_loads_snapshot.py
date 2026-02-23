from core.incidents.snapshotter import IncidentSnapshotter
from core.incidents.replayer import IncidentReplayer

def test_replay_loads_snapshot(temp_artifacts_dir):
    snap = IncidentSnapshotter(base_dir=temp_artifacts_dir)

    incident_id = snap.capture(
        run_id="run-004",
        reason="test",
        payload={"x": 1}
    )

    replayer = IncidentReplayer(base_dir=temp_artifacts_dir)
    snapshot = replayer.load(incident_id)

    assert snapshot["payload"]["x"] == 1
