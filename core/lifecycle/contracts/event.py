from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict

from .state import LifecycleState
from .enums import TransitionReason


@dataclass(frozen=True)
class LifecycleEvent:
    """
    Deterministic lifecycle transition event.

    HARD INVARIANTS (LOCKED):
    - NO UUIDs
    - NO auto-generated IDs
    - NO mutable metadata
    - Equality must be purely structural

    Identity is derived from:
    (strategy_id, from_state, to_state, reason, as_of)
    """

    # ==================================================
    # Core identity (deterministic)
    # ==================================================
    strategy_id: str
    from_state: LifecycleState
    to_state: LifecycleState
    reason: TransitionReason
    as_of: datetime

    # ==================================================
    # Serialization helpers
    # ==================================================
    def to_dict(self) -> Dict[str, Any]:
        """
        Deterministic serialization for journals, evidence, and APIs.
        """
        return {
            "strategy_id": self.strategy_id,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "reason": self.reason.value,
            "as_of": self.as_of.isoformat(),
        }

    # ==================================================
    # Semantic helpers
    # ==================================================
    @property
    def is_promotion(self) -> bool:
        return self.to_state.value > self.from_state.value

    @property
    def is_demotion(self) -> bool:
        return self.to_state.value < self.from_state.value
