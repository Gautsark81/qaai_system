from datetime import datetime, date


class DeterministicContext:
    """
    Freezes time, randomness, and execution context
    for reproducible paper trading runs.
    """

    FIXED_DATE = date(2025, 1, 1)
    FIXED_TIME = datetime(2025, 1, 1, 9, 15)

    @classmethod
    def today(cls):
        return cls.FIXED_DATE

    @classmethod
    def now(cls):
        return cls.FIXED_TIME
