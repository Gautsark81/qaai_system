from datetime import date, time

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig
from core.shadow.scheduler.session import NSESession


def enabled_scheduler():
    return ShadowScheduler(
        config=ShadowSchedulerConfig(enable_shadow_scheduler=True)
    )


def test_shadow_scheduler_blocks_on_nse_holiday():
    scheduler = enabled_scheduler()

    # Gandhi Jayanti (known NSE holiday)
    session = NSESession(
        session_date=date(2024, 10, 2),
        current_time=time(10, 30)
    )

    assert scheduler.should_run(session) is False


def test_shadow_scheduler_allows_regular_trading_day():
    scheduler = enabled_scheduler()

    session = NSESession(
        session_date=date(2024, 10, 3),
        current_time=time(10, 30)
    )

    assert scheduler.should_run(session) is True
