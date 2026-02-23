# core/observability/audit_report.py

from collections import defaultdict
from core.observability.event_store import EventStore


class AuditReport:
    """
    Generates audit summaries.
    """

    def generate(self):
        store = EventStore()
        events = store.load_all()

        summary = defaultdict(int)

        for e in events:
            summary[e["event_type"]] += 1

        return dict(summary)
