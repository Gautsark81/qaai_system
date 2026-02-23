import json
from core.incidents.snapshotter import IncidentSnapshotter

def test_snapshot_metadata_fields(temp_artifacts_dir):
    snap = IncidentSnapshotter(base_dir=temp_artifacts_dir)

    incident_id = snap.capture(
        run_id="run-003",
        reason="latency",
        payload={"latency_ms": 450}
    )

    meta = json.loads(
        (temp_artifacts_dir / f"incident_{incident_id}" / "metadata.json").read_text()
    )

    assert meta["run_id"] == "run-003"
    assert meta["reason"] == "latency"
    assert "timestamp" in meta
