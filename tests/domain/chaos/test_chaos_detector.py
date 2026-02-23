from datetime import datetime
from domain.chaos.chaos_event import ChaosEvent
from domain.chaos.chaos_detector import ChaosDetector


def test_chaos_detector_critical():
    e = ChaosEvent("BROKER_DOWN", "broker", datetime.utcnow(), "lost")
    assert ChaosDetector.is_critical(e) is True
