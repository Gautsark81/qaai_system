from datetime import date, time

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession
from core.governance.reconstruction import reconstruct_system_state


def test_shadow_scheduler_has_no_side_effects():
    config = ShadowSchedulerConfig(enable_shadow_scheduler=True)
    scheduler = ShadowScheduler(config=config)

    session = NSESession(
        session_date=date(2025, 1, 20),
        current_time=time(10, 45)
    )

    before_state = reconstruct_system_state()
    scheduler.evaluate(session)
    after_state = reconstruct_system_state()

    assert before_state == after_state
