# core/observability/event_bus.py

from core.observability.event_store import EventStore
from core.observability.event import Event
from core.state.state_registry import StateRegistry


class EventBus:
    """
    Global event bus.
    """

    _store = EventStore()

    @classmethod
    def emit(
        cls,
        event_type: str,
        payload: dict,
        strategy_id: str | None = None,
        symbol: str | None = None,
    ):
        state = StateRegistry.get()

        event = Event.create(
            event_type=event_type,
            phase=state.phase.value,
            strategy_id=strategy_id,
            symbol=symbol,
            payload=payload,
        )
        cls._store.append(event)
