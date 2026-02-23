from typing import TypedDict, Dict, Any


class Phase1SnapshotContract(TypedDict):
    run_id: str
    mode: str
    uptime_sec: int
    events_processed: int

    safety: Dict[str, Any]
    determinism: Dict[str, Any]
    telemetry: Dict[str, Any]
    violations: Dict[str, Any]

    system_mood: float
