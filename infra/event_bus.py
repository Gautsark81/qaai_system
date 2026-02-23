from __future__ import annotations

"""
Simple synchronous event bus for intra-process orchestration.

Design goals
------------
- Dependency-free
- Extremely lightweight
- Fail-closed: handler errors are logged, never raised
- Supports:
    - subscribe to specific event name
    - subscribe to all events (wildcard)
    - emit events with arbitrary payload objects
- Global singleton via get_global_event_bus() for convenience
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

from infra.logging import get_logger

EventHandler = Callable[["Event"], None]


@dataclass
class Event:
    """
    Generic event container.

    Attributes
    ----------
    name : str
        Event name, e.g. "live.cycle.start", "portfolio.snapshot".
    payload : Mapping[str, Any]
        Event payload – arbitrary data. Can include domain objects
        (Position, Order, PortfolioSnapshot, etc.).
    metadata : Mapping[str, Any]
        Metadata for routing / correlation (env, run_id, strategy_id...).
    ts_ns : int
        Event timestamp in nanoseconds (wall-clock).
    """

    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    ts_ns: int = field(default_factory=time.time_ns)


class EventBus:
    """
    In-process synchronous event bus.

    Handlers are ordinary callables: (Event) -> None.

    Subscriptions
    -------------
    - subscribe(event_name, handler):
        - event_name = "my.event" => handler only sees that event
        - event_name = None       => wildcard; handler sees all events
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []
        self._logger = get_logger("infra.event_bus")

    # ------------------------------------------------------------------ #
    # Subscriptions
    # ------------------------------------------------------------------ #

    def subscribe(
        self,
        event_name: Optional[str],
        handler: EventHandler,
    ) -> None:
        """
        Subscribe a handler to an event.

        Parameters
        ----------
        event_name : str or None
            If None, handler receives all events.
            Otherwise, handler only receives events with this name.
        handler : Callable[[Event], None]
            Callback invoked for matching events.
        """
        if event_name is None:
            self._wildcard_handlers.append(handler)
            return

        self._handlers.setdefault(event_name, []).append(handler)

    # ------------------------------------------------------------------ #
    # Publishing
    # ------------------------------------------------------------------ #

    def publish(self, event: Event) -> None:
        """
        Publish an Event instance to all matching subscribers.
        """
        handlers: List[EventHandler] = list(self._wildcard_handlers)
        handlers.extend(self._handlers.get(event.name, []))

        if not handlers:
            return

        for h in handlers:
            try:
                h(event)
            except Exception:
                # Fail-closed: never let handlers break publishers
                self._logger.exception(
                    "Event handler raised",
                    extra={"event_name": event.name},
                )

    def emit(
        self,
        event_name: str,
        payload: Optional[Mapping[str, Any]] = None,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Convenience wrapper to create and publish an Event.

        Example:
            bus.emit(
                "portfolio.snapshot",
                payload={"snapshot": snapshot},
                metadata={"run_id": run_id},
            )
        """
        event = Event(
            name=event_name,
            payload=payload or {},
            metadata=metadata or {},
        )
        self.publish(event)


# ---------------------------------------------------------------------- #
# Global singleton
# ---------------------------------------------------------------------- #

_global_bus: Optional[EventBus] = None


def get_global_event_bus() -> EventBus:
    """
    Return the process-wide default EventBus instance.

    This avoids threading an EventBus through every function signature.
    Advanced setups can choose to ignore this and create their own
    EventBus instances.
    """
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus
