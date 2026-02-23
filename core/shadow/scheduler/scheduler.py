from typing import Tuple

from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession
from core.shadow.scheduler.calendar import NSEHolidayCalendar
from core.shadow.scheduler.models import ShadowSchedulerEvent


class ShadowScheduler:
    """
    Shadow Scheduler — Phase 13.1

    Responsibilities:
    - Bind shadow execution to NSE market sessions
    - Require explicit enablement
    - Be holiday aware
    - Emit observational audit evidence only
    - Remain pure, deterministic, and replay-safe
    """

    def __init__(self, config: ShadowSchedulerConfig | None = None) -> None:
        self._config = config or ShadowSchedulerConfig()

    @property
    def is_enabled(self) -> bool:
        return bool(self._config.enable_shadow_scheduler)

    def should_run(self, session: NSESession) -> bool:
        """
        Determines whether shadow logic should run
        for the given NSE session context.
        """
        if not self.is_enabled:
            return False

        if NSEHolidayCalendar.is_holiday(session.session_date):
            return False

        if not session.is_market_hours:
            return False

        return True

    def evaluate(self, session: NSESession) -> Tuple[ShadowSchedulerEvent, ...]:
        """
        Evaluate scheduler state for the given session.

        Returns:
            Tuple of observational audit events only.
        """
        if not self.should_run(session):
            return ()

        event = ShadowSchedulerEvent(
            kind="SHADOW_SCHEDULER",
            is_observational=True,
            has_execution_authority=False,
            has_capital_authority=False,
        )

        return (event,)
