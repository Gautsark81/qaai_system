from dataclasses import dataclass
from datetime import datetime
from core.strategy_factory.lifecycle.state_machine import LifecycleState


@dataclass(frozen=True)
class LifecycleEvent:
    strategy_dna: str
    from_state: LifecycleState
    to_state: LifecycleState
    trigger: str
    reason: str
    timestamp: datetime = datetime.utcnow()
    lifecycle_version: str = "v4-phase9"
