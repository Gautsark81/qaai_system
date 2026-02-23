from datetime import date


class NSEHolidayCalendar:
    """
    Minimal NSE holiday calendar.

    This is intentionally explicit and deterministic.
    It can be extended later, but Phase 13.1 requires correctness,
    not coverage breadth.
    """

    _HOLIDAYS = {
        # Gandhi Jayanti
        date(2024, 10, 2),
    }

    @classmethod
    def is_holiday(cls, session_date: date) -> bool:
        return session_date in cls._HOLIDAYS
