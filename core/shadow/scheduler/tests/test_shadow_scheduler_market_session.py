from datetime import datetime, time, date

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession


def enabled_scheduler():
    return ShadowScheduler(
        config=ShadowSchedulerConfig(enable_shadow_scheduler=True)
    )


def test_shadow_scheduler_blocks_before_market_open():
    scheduler = enabled_scheduler()

    session = NSESession(
        session_date=date(2025, 1, 10),
        current_time=time(8, 30)
    )

    assert scheduler.should_run(session) is False


def test_shadow_scheduler_allows_during_market_hours():
    scheduler = enabled_scheduler()

    session = NSESession(
        session_date=date(2025, 1, 10),
        current_time=time(10, 15)
    )

    assert scheduler.should_run(session) is True


def test_shadow_scheduler_blocks_after_market_close():
    scheduler = enabled_scheduler()

    session = NSESession(
        session_date=date(2025, 1, 10),
        current_time=time(16, 0)
    )

    assert scheduler.should_run(session) is False
