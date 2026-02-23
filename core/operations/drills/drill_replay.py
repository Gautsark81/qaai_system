from core.operations.ops_store import OpsEventStore


class DrillReplayValidator:
    """
    Validates that drills can be replayed from ops logs.
    """

    def __init__(self, ops_store: OpsEventStore | None = None):
        self.ops_store = ops_store or OpsEventStore()

    def list_drills(self):
        return [
            e for e in self.ops_store.load_all()
            if e["event_type"].startswith("drill_")
        ]
