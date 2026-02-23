from datetime import date, time

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession


def test_shadow_scheduler_is_deterministic():
    config = ShadowSchedulerConfig(enable_shadow_scheduler=True)

    scheduler_1 = ShadowScheduler(config=config)
    scheduler_2 = ShadowScheduler(config=config)

    session = NSESession(
        session_date=date(2025, 1, 15),
        current_time=time(11, 0)
    )

    result_1 = scheduler_1.evaluate(session)
    result_2 = scheduler_2.evaluate(session)

    assert result_1 == result_2
