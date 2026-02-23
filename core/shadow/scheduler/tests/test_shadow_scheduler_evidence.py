from datetime import date, time

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession


def test_shadow_scheduler_emits_audit_evidence_only():
    scheduler = ShadowScheduler(
        config=ShadowSchedulerConfig(enable_shadow_scheduler=True)
    )

    session = NSESession(
        session_date=date(2025, 1, 22),
        current_time=time(11, 30)
    )

    events = scheduler.evaluate(session)

    assert isinstance(events, tuple)

    for event in events:
        assert event.kind == "SHADOW_SCHEDULER"
        assert event.is_observational is True
        assert event.has_execution_authority is False
        assert event.has_capital_authority is False
