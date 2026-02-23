from domain.chaos.chaos_event import ChaosEvent


class ChaosDetector:
    """
    Detects whether chaos conditions exist.
    """

    CRITICAL_EVENTS = {
        "BROKER_DOWN",
        "FEED_GAP",
    }

    @staticmethod
    def is_critical(event: ChaosEvent) -> bool:
        return event.event_type in ChaosDetector.CRITICAL_EVENTS
