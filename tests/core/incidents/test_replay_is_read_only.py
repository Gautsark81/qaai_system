import pytest
from core.incidents.snapshotter import IncidentSnapshotter
from core.incidents.replayer import IncidentReplayer

def test_replay_is_read_only(temp_artifacts_dir):
    snap = IncidentSnapshotter(base_dir=temp_artifacts_dir)
    incident_id = snap.capture("run-005", "readonly", {})

    replayer = IncidentReplayer(base_dir=temp_artifacts_dir)

    with pytest.raises(RuntimeError):
        replayer.modify(incident_id)
