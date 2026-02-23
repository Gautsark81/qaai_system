from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ==========================================================
# SNAPSHOTS (IMMUTABLE)
# ==========================================================

@dataclass(frozen=True)
class HealthSnapshot:
    step: int
    health_score: float
    signals: Dict[str, float]
    flags: List[str]


@dataclass(frozen=True)
class DecaySnapshot:
    step: int
    level: str
    reasons: List[str]
    windows_confirmed: List[int]


@dataclass(frozen=True)
class StateSnapshot:
    step: int
    state: str
    reason: Optional[str]


# ==========================================================
# STRATEGY TELEMETRY CONTAINER
# ==========================================================

@dataclass
class StrategyTelemetry:
    """
    Append-only telemetry container.
    NEVER mutates or deletes history.
    """

    strategy_id: str

    health: List[HealthSnapshot] = field(default_factory=list)
    decay: List[DecaySnapshot] = field(default_factory=list)
    state: List[StateSnapshot] = field(default_factory=list)

    # ------------------------------------------------------
    # Derived Views (Read-Only)
    # ------------------------------------------------------

    def last_health(self) -> Optional[HealthSnapshot]:
        return self.health[-1] if self.health else None

    def last_decay(self) -> Optional[DecaySnapshot]:
        return self.decay[-1] if self.decay else None

    def last_state(self) -> Optional[StateSnapshot]:
        return self.state[-1] if self.state else None

    def state_timeline(self) -> List[str]:
        return [s.state for s in self.state]

    def pause_events(self) -> List[StateSnapshot]:
        return [s for s in self.state if s.state == "PAUSED"]

    def decay_events(self) -> List[DecaySnapshot]:
        return [d for d in self.decay if d.level != "NO_DECAY"]
