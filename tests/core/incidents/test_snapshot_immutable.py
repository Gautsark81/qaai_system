import pytest
from core.incidents.snapshotter import IncidentSnapshotter

def test_snapshot_is_immutable(temp_artifacts_dir):
    snap = IncidentSnapshotter(base_dir=temp_artifacts_dir)

    incident_id = snap.capture(
        run_id="run-002",
        reason="risk-breach",
        payload={}
    )

    with pytest.raises(RuntimeError):
        snap.capture(
            run_id="run-002",
            reason="second",
            payload={}
        )
