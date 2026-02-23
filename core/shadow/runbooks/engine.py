from typing import List, Dict, Any

from core.shadow.runbooks.config import ShadowRunbookConfig
from core.shadow.runbooks.models import RunbookEvent
from core.shadow.runbooks.report import RunbookReport


class ShadowRunbookEngine:
    """
    Phase 13.4 — Shadow Runbooks Engine.

    Executes operator drills in shadow mode.
    Produces deterministic, replayable runbook evidence.
    """

    def __init__(self, *, config: ShadowRunbookConfig | None = None):
        self._config = config or ShadowRunbookConfig()

    @property
    def is_enabled(self) -> bool:
        return bool(self._config.enable_shadow_runbooks)

    def execute(
        self,
        runbook: str,
        *,
        operator_ack: bool = False,
    ) -> RunbookReport:
        if not self.is_enabled:
            return RunbookReport(
                executed=False,
                events=[],
                operator_acknowledged=False,
                evidence={},
            )

        events: List[RunbookEvent] = []

        if runbook == RunbookEvent.FORCED_SHUTDOWN:
            events.append(RunbookEvent.FORCED_SHUTDOWN)

        elif runbook == RunbookEvent.GRACEFUL_HALT:
            events.append(RunbookEvent.GRACEFUL_HALT)

        elif runbook == RunbookEvent.RECOVERY_REPLAY:
            events.append(RunbookEvent.RECOVERY_REPLAY)

        evidence: Dict[str, Any] = {
            "runbook": runbook,
            "events": [e.value for e in events],
        }

        return RunbookReport(
            executed=True,
            events=events,
            operator_acknowledged=bool(operator_ack),
            evidence=evidence,
            has_execution_authority=False,
            has_capital_authority=False,
        )
