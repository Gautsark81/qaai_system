# core/observability/replay_engine.py

from core.observability.event_store import EventStore


class ReplayEngine:
    """
    Replays system events for audit/debug.
    """

    def __init__(self):
        self.store = EventStore()

    def replay(self, filter_fn=None):
        events = self.store.load_all()
        for event in events:
            if filter_fn and not filter_fn(event):
                continue
            yield event
