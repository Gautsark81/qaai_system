from datetime import datetime
from domain.observability.event_log import EventLog, SystemEvent


def test_event_logged():
    log = EventLog()
    log.record(
        SystemEvent(datetime.utcnow(), "INFO", "data", "Feed connected")
    )
    assert len(log.all()) == 1
