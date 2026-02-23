from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class Phase1SystemState:
    # Identity
    run_id: str
    mode: str

    # Time
    boot_timestamp: datetime
    last_heartbeat_ts: Optional[datetime]
    uptime_sec: int

    # Safety
    execution_possible: bool
    capital_allocated: float
    kill_switch_state: str

    # Determinism
    intent_count: int
    determinism_hashes: List[str]
    replay_match_rate: float

    # Telemetry
    telemetry_expected: int
    telemetry_written: int
    telemetry_completeness: float

    # Violations
    violation_count: int
    violation_rate: float
    last_violation_ts: Optional[datetime]

    # Intelligence
    system_mood_index: float
    violation_pulse: float

    @classmethod
    def initial(cls) -> "Phase1SystemState":
        return cls(
            run_id="bootstrap",
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
