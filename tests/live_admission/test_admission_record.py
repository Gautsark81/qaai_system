from datetime import datetime, timedelta
from modules.live_admission.admission_record import LiveAdmissionRecord


def test_admission_active():
    now = datetime.utcnow()
    record = LiveAdmissionRecord(
        "s1", 100_000, now, now + timedelta(hours=6), "tok1"
    )
    assert record.is_active(now)


def test_admission_expired():
    now = datetime.utcnow()
    record = LiveAdmissionRecord(
        "s1", 100_000, now - timedelta(hours=10),
        now - timedelta(hours=1), "tok1"
    )
    assert not record.is_active(now)
