from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class NSESession:
    """
    Immutable representation of an NSE market session.
    """
    session_date: date
    current_time: time

    @property
    def is_market_hours(self) -> bool:
        """
        NSE regular trading hours:
        09:15 IST – 15:30 IST
        """
        return time(9, 15) <= self.current_time <= time(15, 30)
