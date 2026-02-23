from datetime import datetime, timezone

from core.operations.ops_store import OpsEventStore
from core.operations.ops_events import OpsEvent
from core.operations.drills.drill_contract import OpsDrill


class OpsDrillRunner:
    """
    Executes operational drills in DRY-RUN mode.
    No live execution is touched.
    """

    def __init__(self, ops_store: OpsEventStore | None = None):
        self.ops_store = ops_store or OpsEventStore()

    def run(self, drill: OpsDrill) -> None:
        self.ops_store.append(
            OpsEvent.now(
                event_type=f"drill_{drill.drill_type}",
                operator=drill.initiated_by,
                notes=(
                    f"O-1.5 DRILL | target={drill.target} | "
                    f"expected={drill.expected_response} | "
                    f"{drill.notes or ''}"
                ),
            )
        )
