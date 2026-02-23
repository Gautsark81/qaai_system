# infra/time_utils.py
from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

# Trading session rules from MASTER spec
TRADING_START_IST = time(9, 30)
BLOCK_NEW_ENTRIES_IST = time(14, 30)
FORCE_EXIT_IST = time(15, 15)


def now_ist() -> datetime:
    """Current time in IST, timezone-aware."""
    return datetime.now(IST)


def to_ist(dt: datetime) -> datetime:
    """
    Convert any datetime to IST.
    - Naive datetimes are assumed to be UTC.
    - Aware datetimes are converted via .astimezone(IST).
    """
    if dt.tzinfo is None:
        # assume UTC
        return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(IST)
    return dt.astimezone(IST)


def is_trading_session_open(dt: Optional[datetime] = None) -> bool:
    """
    Returns True if we are within the trading window:
    09:30 <= t < 15:15 IST
    (Entries allowed until 14:30, forced exit at 15:15.)
    """
    if dt is None:
        dt = now_ist()
    else:
        dt = to_ist(dt)

    t = dt.time()
    return TRADING_START_IST <= t < FORCE_EXIT_IST
