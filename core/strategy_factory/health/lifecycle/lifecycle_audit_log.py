from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)


@dataclass(frozen=True)
class LifecycleAuditEvent:
    """
    Immutable, advisory-only lifecycle audit event.
    """

    strategy_id: str
    previous_action: Optional[StrategyLifecycleAction]
    current_action: StrategyLifecycleAction
    timestamp: datetime
    reasons: List[str]

    advisory_only: bool = field(init=False, default=True)
    source: str = field(init=False, default="StrategyLifecycleController")
    event_id: str = field(init=False)

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (UTC)")

        event_id = self._compute_event_id()
        object.__setattr__(self, "event_id", event_id)

    def _compute_event_id(self) -> str:
        payload = "|".join(
            [
                self.strategy_id,
                str(self.previous_action),
                str(self.current_action),
                self.timestamp.isoformat(),
                ",".join(self.reasons),
                self.source,
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class LifecycleAuditLog:
    """
    Append-only, deterministic audit log for lifecycle events.
    """

    def __init__(self):
        self._events: List[LifecycleAuditEvent] = []
        self._last_action: Dict[str, StrategyLifecycleAction] = {}

    # ----------------------------
    # Recording
    # ----------------------------

    def record(
        self,
        *,
        strategy_id: str,
        previous_action: Optional[StrategyLifecycleAction],
        current_action: StrategyLifecycleAction,
        reasons: List[str],
        timestamp: Optional[datetime] = None,
    ) -> None:
        ts = timestamp or datetime.now(timezone.utc)

        # No-op if no change
        if (
            strategy_id in self._last_action
            and self._last_action[strategy_id] == current_action
        ):
            return

        event = LifecycleAuditEvent(
            strategy_id=strategy_id,
            previous_action=previous_action,
            current_action=current_action,
            timestamp=ts,
            reasons=reasons,
        )

        self._events.append(event)
        self._last_action[strategy_id] = current_action

    # ----------------------------
    # Query
    # ----------------------------

    def all_events(self) -> List[LifecycleAuditEvent]:
        return list(self._events)

    def events_for_strategy(self, strategy_id: str) -> List[LifecycleAuditEvent]:
        return [e for e in self._events if e.strategy_id == strategy_id]
