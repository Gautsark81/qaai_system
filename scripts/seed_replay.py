from pathlib import Path
from datetime import datetime

from core.execution.replay.models import ReplayIdentity, ReplayMode
from core.execution.replay.inputs import ReplayInputs
from core.execution.replay.envelope import ReplayEnvelope
from core.execution.replay.deterministic_engine import DeterministicReplayEngine
from core.execution.replay.diff_engine import diff_replay_vs_live
from core.execution.replay.fs_store import FileSystemReplayStore

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.telemetry import ExecutionTelemetry, ExecutionEvent
from core.execution.invariant_validator import validate_execution_invariants


# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

EXECUTION_ID = "EXEC_TEST_001"
REPLAY_ID = "REPLAY_TEST_001"

TELEMETRY_FILE = Path("data/telemetry/EXEC_TEST_001.jsonl")
REPLAY_STORE_DIR = Path("data/replay")


# ------------------------------------------------------------------
# Load synthetic telemetry records
# ------------------------------------------------------------------

records = []
with TELEMETRY_FILE.open() as f:
    for line in f:
        records.append(eval(line))  # safe here: controlled synthetic data


# ------------------------------------------------------------------
# Build live telemetry snapshot (as if execution happened)
# ------------------------------------------------------------------

events = [
    ExecutionEvent(
        timestamp=datetime.fromisoformat(r["timestamp"]),
        event_type=r["event_type"],
        message=r["message"],
    )
    for r in records
]

live_telemetry = ExecutionTelemetry(
    execution_id=EXECUTION_ID,
    started_at=events[0].timestamp,
    completed_at=events[-1].timestamp,
    total_orders=1,
    filled_orders=1,
    rejected_orders=0,
    cancelled_orders=0,
    events=tuple(events),
)

live_snapshot = ExecutionTelemetrySnapshot(
    telemetry=live_telemetry,
    invariants=validate_execution_invariants(live_telemetry),
)


# ------------------------------------------------------------------
# Build replay envelope
# ------------------------------------------------------------------

identity = ReplayIdentity(
    replay_id=REPLAY_ID,
    execution_id=EXECUTION_ID,
    requested_at=datetime.utcnow(),
    mode=ReplayMode.FULL_REPLAY,
)

inputs = ReplayInputs(
    telemetry_records=tuple(records),
    config_snapshot={
        "total_orders": 1,
        "filled_orders": 1,
        "rejected_orders": 0,
        "cancelled_orders": 0,
    },
    environment={
        "started_at": events[0].timestamp.isoformat(),
    },
)

envelope = ReplayEnvelope(identity=identity, inputs=inputs)


# ------------------------------------------------------------------
# Run replay
# ------------------------------------------------------------------

engine = DeterministicReplayEngine()
replay_result = engine.run(envelope)

diff_report = diff_replay_vs_live(
    live=live_snapshot,
    replay=replay_result,
)


# ------------------------------------------------------------------
# Persist replay artifacts
# ------------------------------------------------------------------

store = FileSystemReplayStore(REPLAY_STORE_DIR)

store.append_result(replay_result)
store.append_diff(diff_report)

print("✅ Synthetic replay seeded successfully")
