from datetime import datetime
from dashboard.domain.phase1_state import Phase1SystemState
from dashboard.services.phase1_snapshot_builder import Phase1SnapshotBuilder

state = Phase1SystemState(
    run_id="manual_check",
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

builder = Phase1SnapshotBuilder(state)

builder.ingest({
    "event_type": "ExecutionIntentCreated",
    "timestamp": datetime.utcnow(),
    "determinism_hash": "debug_hash_001",
})

snapshot = builder.build_snapshot()
print(snapshot)
