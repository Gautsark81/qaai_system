from datetime import datetime

from core.strategy_factory.health.notifications.notifications_router import (
    Notification,
    NotificationChannel,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)


def test_notification_is_advisory_and_channel_bound():
    notification = Notification(
        strategy_id="STRAT_009",
        channel=NotificationChannel.CONSOLE,
        message="Health degraded",
        timestamp=datetime.utcnow(),
        action=StrategyLifecycleAction.DEMOTE,
    )

    assert notification.advisory_only is True
    assert notification.channel == NotificationChannel.CONSOLE
