def test_snapshot_contract_shape(snapshot):
    required_keys = {
        "run_id",
        "mode",
        "uptime_sec",
        "safety",
        "determinism",
        "telemetry",
        "violations",
        "system_mood",
        "events_processed",
    }
    assert required_keys.issubset(snapshot.keys())
