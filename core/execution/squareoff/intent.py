from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class SquareOffIntent:
    """
    Trigger-level intent explaining WHY a square-off is required.
    """
    reason: str
    audit_id: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def create(cls, reason: str) -> "SquareOffIntent":
        return cls(
            reason=reason,
            audit_id=f"AUDIT-{uuid4().hex[:8].upper()}",
        )
