from core.incidents.snapshotter import IncidentSnapshotter

def test_snapshot_created_on_incident(temp_artifacts_dir):
    snap = IncidentSnapshotter(base_dir=temp_artifacts_dir)

    incident_id = snap.capture(
        run_id="run-001",
        reason="kill-switch",
        payload={"symbol": "RELIANCE"}
    )

    path = temp_artifacts_dir / f"incident_{incident_id}"
    assert path.exists()
    assert (path / "metadata.json").exists()
