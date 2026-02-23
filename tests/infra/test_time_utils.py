# tests/infra/test_time_utils.py
from datetime import datetime, timezone

from infra.time_utils import (
    IST,
    now_ist,
    to_ist,
    is_trading_session_open,
    TRADING_START_IST,
    FORCE_EXIT_IST,
)


def test_now_ist_timezone():
    now = now_ist()
    assert now.tzinfo == IST


def test_to_ist_from_utc_naive():
    dt_utc = datetime(2025, 1, 1, 9, 0, 0)  # naive, assume UTC
    dt_ist = to_ist(dt_utc)
    assert dt_ist.tzinfo == IST
    # UTC 09:00 -> IST 14:30
    assert dt_ist.hour == 14


def test_to_ist_from_aware():
    dt_utc = datetime(2025, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    dt_ist = to_ist(dt_utc)
    assert dt_ist.tzinfo == IST
    assert dt_ist.hour == 14


def test_is_trading_session_open_boundaries():
    start_dt = datetime(2025, 1, 1, TRADING_START_IST.hour, TRADING_START_IST.minute, tzinfo=IST)
    assert is_trading_session_open(start_dt)

    end_dt = datetime(2025, 1, 1, FORCE_EXIT_IST.hour, FORCE_EXIT_IST.minute, tzinfo=IST)
    assert not is_trading_session_open(end_dt)
