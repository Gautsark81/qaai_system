from datetime import datetime
from dashboard.domain.phase1_state import Phase1SystemState
from dashboard.services.phase1_snapshot_builder import Phase1SnapshotBuilder

def base_state():
    return Phase1SystemState(
        run_id="shadow_test",
        mode="paper",
        boot_timestamp=datetime.utcnow(),
        last_heartbeat_ts=None,
        uptime_sec=0,
        execution_possible=False,
        capital_allocated=0.0,
        kill_switch_state="armed",
        intent_count=0,
        determinism_hashes=[],
        replay_match_rate=1.0,
        telemetry_expected=0,
        telemetry_written=0,
        telemetry_completeness=1.0,
        violation_count=0,
        violation_rate=0.0,
        last_violation_ts=None,
        system_mood_index=100.0,
        violation_pulse=0.0,
    )

def test_snapshot_builds_cleanly():
    builder = Phase1SnapshotBuilder(base_state())

    builder.ingest({
        "event_type": "ExecutionIntentCreated",
        "timestamp": datetime.utcnow(),
        "determinism_hash": "abc123"
    })

    snapshot = builder.build_snapshot()

    assert snapshot["determinism"]["intent_count"] == 1
    assert snapshot["system_mood"] > 90
