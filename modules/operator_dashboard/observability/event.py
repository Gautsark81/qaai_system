# core/observability/event.py

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: str
    event_type: str
    phase: str
    strategy_id: str | None
    symbol: str | None
    payload: dict

    @staticmethod
    def create(
        event_type: str,
        phase: str,
        payload: dict,
        strategy_id: str | None = None,
        symbol: str | None = None,
    ) -> "Event":
        return Event(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            phase=phase,
            strategy_id=strategy_id,
            symbol=symbol,
            payload=payload,
        )
