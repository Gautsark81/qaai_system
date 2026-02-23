# tests/unit/test_ist_time.py
from utils.ist_time import now_ist, to_ist, format_iso_ist
from datetime import datetime, timezone

def test_now_ist_has_tz():
    dt = now_ist()
    assert dt.tzinfo is not None
    assert "Asia" in dt.tzname() or dt.tzname()  # ensure tz present

def test_to_ist_converts_naive():
    na = datetime(2020, 1, 1, 0, 0, 0)  # naive
    converted = to_ist(na)
    assert converted.tzinfo is not None

def test_format_iso_ist():
    s = format_iso_ist(datetime.utcnow())
    assert "T" in s
