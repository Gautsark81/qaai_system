from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set, Tuple

from core.strategy_factory.health.lifecycle.lifecycle_audit_log import (
    LifecycleAuditEvent,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)


class NotificationChannel(str, Enum):
    CONSOLE = "CONSOLE"
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    WEBHOOK = "WEBHOOK"


@dataclass(frozen=True)
class Notification:
    """
    Advisory-only notification derived from lifecycle events.
    Backward-compatible with earlier phases.
    """

    strategy_id: str
    channel: NotificationChannel
    message: str
    timestamp: datetime
    action: Optional[StrategyLifecycleAction] = None

    advisory_only: bool = field(init=False, default=True)


@dataclass(frozen=True)
class NotificationSubscription:
    """
    Declarative subscription filter.
    """

    channel: NotificationChannel
    strategy_ids: Optional[Set[str]] = None
    actions: Optional[Set[StrategyLifecycleAction]] = None

    def matches(self, event: LifecycleAuditEvent) -> bool:
        if self.strategy_ids is not None and event.strategy_id not in self.strategy_ids:
            return False

        if self.actions is not None and event.current_action not in self.actions:
            return False

        return True

    def fingerprint(self) -> Tuple:
        return (
            self.channel,
            frozenset(self.strategy_ids) if self.strategy_ids is not None else None,
            frozenset(self.actions) if self.actions is not None else None,
        )


class NotificationsRouter:
    """
    Deterministic, advisory-only notification router.
    """

    def __init__(self, *, subscriptions: List[NotificationSubscription]):
        self._subscriptions = subscriptions
        self._notifications: List[Notification] = []
        self._seen: Set[Tuple[str, Tuple]] = set()

    # ----------------------------
    # Processing
    # ----------------------------

    def process_event(self, event: LifecycleAuditEvent) -> None:
        for sub in self._subscriptions:
            if not sub.matches(event):
                continue

            key = (event.event_id, sub.fingerprint())
            if key in self._seen:
                continue

            notification = Notification(
                strategy_id=event.strategy_id,
                channel=sub.channel,
                message=self._render_message(event),
                timestamp=event.timestamp,
                action=event.current_action,
            )

            self._notifications.append(notification)
            self._seen.add(key)

    # ----------------------------
    # Query
    # ----------------------------

    def notifications(self) -> List[Notification]:
        return list(self._notifications)

    # ----------------------------
    # Rendering
    # ----------------------------

    def _render_message(self, event: LifecycleAuditEvent) -> str:
        reasons = "; ".join(event.reasons)
        return (
            f"[{event.current_action}] "
            f"Strategy {event.strategy_id}: {reasons}"
        )
