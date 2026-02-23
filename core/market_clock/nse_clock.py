from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from .session_state import NSESessionState

# -------------------------------------------------
# TIMEZONE
# -------------------------------------------------

IST = timezone(timedelta(hours=5, minutes=30))


def _seconds_since_midnight(dt: datetime) -> int:
    """
    Convert datetime to seconds since midnight (exchange local time).
    Deterministic and timezone-safe.
    """
    local = dt.astimezone(IST)
    return local.hour * 3600 + local.minute * 60 + local.second


# -------------------------------------------------
# NSE MARKET CLOCK
# -------------------------------------------------

@dataclass(frozen=True)
class NSEMarketClock:
    """
    Deterministic NSE market clock.

    Guarantees:
    - Second-level precision
    - Timezone safe (IST)
    - Pure & immutable
    - Test-safe constructors
    """

    _now: datetime
    _is_holiday: bool = False

    # -------------------------------------------------
    # TEST FACTORIES (SAFE)
    # -------------------------------------------------

    @classmethod
    def for_test(cls, t: time) -> "NSEMarketClock":
        """
        Deterministic test constructor using exchange-local time.
        """
        dt = datetime.combine(date.today(), t, tzinfo=IST)
        return cls(_now=dt, _is_holiday=False)

    @classmethod
    def for_test_date(
        cls,
        *,
        trade_date: date,
        is_holiday: bool,
    ) -> "NSEMarketClock":
        """
        Deterministic test constructor for holiday logic.
        """
        dt = datetime.combine(trade_date, time(9, 15), tzinfo=IST)
        return cls(_now=dt, _is_holiday=is_holiday)

    @classmethod
    def for_test_time(cls, t: datetime) -> "NSEMarketClock":
        """
        Deterministic test-only constructor using absolute time (UTC or IST).

        Required for safety guards that compare absolute timestamps
        (e.g. BrokerTimeDriftGuard).
        """
        if t.tzinfo is None:
            raise ValueError("Test datetime must be timezone-aware")

        return cls(
            _now=t.astimezone(IST),
            _is_holiday=False,
        )

    # -------------------------------------------------
    # ABSOLUTE TIME (FOR SAFETY)
    # -------------------------------------------------

    @property
    def now_utc(self) -> datetime:
        """
        Absolute NSE clock time in UTC.
        Required for cross-system drift detection.
        """
        return self._now.astimezone(timezone.utc)

    # -------------------------------------------------
    # SESSION STATE
    # -------------------------------------------------

    @property
    def session_state(self) -> NSESessionState:
        if self._is_holiday:
            return NSESessionState.CLOSED

        s = _seconds_since_midnight(self._now)

        PRE_OPEN_START = 9 * 3600
        OPEN_TICK = 9 * 3600 + 15 * 60          # 09:15:00
        NORMAL_START = OPEN_TICK + 5            # 09:15:05
        SQUARE_OFF_START = 15 * 3600 + 15 * 60  # 15:15:00
        CLOSE_TIME = 15 * 3600 + 30 * 60        # 15:30:00

        if s < PRE_OPEN_START:
            return NSESessionState.CLOSED

        if PRE_OPEN_START <= s < OPEN_TICK:
            return NSESessionState.PRE_OPEN

        if s == OPEN_TICK:
            return NSESessionState.OPEN

        if OPEN_TICK < s < NORMAL_START:
            return NSESessionState.OPEN  # open buffer (blocked)

        if NORMAL_START <= s < SQUARE_OFF_START:
            return NSESessionState.NORMAL

        if SQUARE_OFF_START <= s < CLOSE_TIME:
            return NSESessionState.SQUARE_OFF_BUFFER

        return NSESessionState.CLOSED

    # -------------------------------------------------
    # HARD SAFETY GATES
    # -------------------------------------------------

    def assert_execution_allowed(self) -> None:
        state = self.session_state

        if state in (
            NSESessionState.CLOSED,
            NSESessionState.PRE_OPEN,
            NSESessionState.OPEN,
        ):
            raise RuntimeError(
                f"Execution blocked during NSE session state: {state}"
            )

    def assert_new_position_allowed(self) -> None:
        if self.session_state != NSESessionState.NORMAL:
            raise RuntimeError(
                f"New positions blocked during NSE session state: {self.session_state}"
            )
