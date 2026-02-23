from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from .state import LifecycleState


@dataclass(frozen=True)
class LifecycleSnapshot:
    """
    Immutable snapshot of a strategy's lifecycle state.

    Guarantees:
    - Deterministic (no derived fields)
    - Replay-safe (sufficient to rebuild lifecycle history)
    - Versioned (schema evolution supported)
    - Audit-ready (explicit timestamps only)
    """

    # Stable strategy identifier (DNA / registry key)
    strategy_id: str

    # Current lifecycle state
    state: LifecycleState

    # Timestamp when this state became active
    since: datetime

    # Lifecycle schema / rule version
    version: str

    # --------------------------------------------------
    # Serialization helpers (explicit & safe)
    # --------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert snapshot to a JSON-safe dictionary.
        """
        return {
            "strategy_id": self.strategy_id,
            "state": self.state.value,
            "since": self.since.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LifecycleSnapshot":
        """
        Rehydrate snapshot from a dictionary.
        """
        return cls(
            strategy_id=data["strategy_id"],
            state=LifecycleState(data["state"]),
            since=datetime.fromisoformat(data["since"]),
            version=data["version"],
        )
