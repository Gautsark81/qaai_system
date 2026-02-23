from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class MarketSession:
    """
    Immutable market session context.

    This is an injected, replayable view of market time.
    """
    session_date: date
    current_time: time
