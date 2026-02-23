# utils/ist_time.py
"""
Utilities for IST-aware timestamps and conversions.
All times produced by these helpers are timezone-aware (tzinfo set).
"""

from datetime import datetime, timezone, timedelta
import zoneinfo

# Asia/Kolkata zoneinfo name
IST = zoneinfo.ZoneInfo("Asia/Kolkata")


def now_ist() -> datetime:
    """Return current time with IST tzinfo."""
    return datetime.now(IST)


def to_ist(dt: datetime) -> datetime:
    """Convert a datetime (naive or aware) to IST tz-aware datetime."""
    if dt.tzinfo is None:
        # assume UTC for naive objects to get a deterministic conversion
        return dt.replace(tzinfo=timezone.utc).astimezone(IST)
    else:
        return dt.astimezone(IST)


def format_iso_ist(dt: datetime) -> str:
    """Return ISO 8601 formatted string in IST with offset."""
    return to_ist(dt).isoformat()


# small convenience function for tests
def parse_iso_to_ist(s: str) -> datetime:
    # parse using fromisoformat (python >=3.7)
    dt = datetime.fromisoformat(s)
    return to_ist(dt)
