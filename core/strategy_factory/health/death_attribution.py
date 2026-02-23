from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from core.strategy_factory.health.death_reason import DeathReason


@dataclass(frozen=True)
class DeathAttribution:
    """
    Immutable record describing why and how a strategy died.

    This object is:
    - Auditable
    - Serializable
    - Learning-safe
    - Write-once
    """

    strategy_id: str
    reason: DeathReason
    timestamp: datetime
    triggered_by: str
    metrics: Dict[str, Any]

    def __repr__(self) -> str:
        return (
            f"DeathAttribution("
            f"strategy_id={self.strategy_id!r}, "
            f"reason={self.reason.value!r}, "
            f"timestamp={self.timestamp.isoformat()}, "
            f"triggered_by={self.triggered_by!r}, "
            f"metrics_keys={list(self.metrics.keys())!r}"
            f")"
        )
