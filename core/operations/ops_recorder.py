from core.operations.ops_events import OpsEvent
from core.operations.ops_store import OpsEventStore


class OpsRecorder:
    """
    Safe façade for Phase O-1 operations.
    """

    def __init__(self, operator: str, store: OpsEventStore | None = None):
        self.operator = operator
        self.store = store or OpsEventStore()

    def record_daily_check(self, notes: str) -> None:
        self.store.append(
            OpsEvent.now(
                event_type="daily_check",
                operator=self.operator,
                notes=notes,
            )
        )

    def record_weekly_check(self, notes: str) -> None:
        self.store.append(
            OpsEvent.now(
                event_type="weekly_check",
                operator=self.operator,
                notes=notes,
            )
        )

    def record_kill_switch_drill(self, notes: str) -> None:
        self.store.append(
            OpsEvent.now(
                event_type="kill_switch_drill",
                operator=self.operator,
                notes=notes,
            )
        )

    def record_governance_dry_run(self, notes: str) -> None:
        self.store.append(
            OpsEvent.now(
                event_type="governance_dry_run",
                operator=self.operator,
                notes=notes,
            )
        )
