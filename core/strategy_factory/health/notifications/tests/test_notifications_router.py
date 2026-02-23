from datetime import datetime, timezone

from core.strategy_factory.health.lifecycle.lifecycle_audit_log import (
    LifecycleAuditEvent,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)
from core.strategy_factory.health.notifications.notifications_router import (
    Notification,
    NotificationChannel,
    NotificationSubscription,
    NotificationsRouter,
)


def utc_now():
    return datetime.now(timezone.utc)


def make_event(strategy_id, action):
    return LifecycleAuditEvent(
        strategy_id=strategy_id,
        previous_action=None,
        current_action=action,
        timestamp=utc_now(),
        reasons=["test reason"],
    )


def test_notification_is_advisory_only():
    n = Notification(
        strategy_id="s1",
        channel=NotificationChannel.CONSOLE,
        message="hello",
        timestamp=utc_now(),
    )

    assert n.advisory_only is True


def test_subscription_filters_by_strategy_and_action():
    sub = NotificationSubscription(
        channel=NotificationChannel.CONSOLE,
        strategy_ids={"s1"},
        actions={StrategyLifecycleAction.PROMOTE},
    )

    router = NotificationsRouter(subscriptions=[sub])

    event_ok = make_event("s1", StrategyLifecycleAction.PROMOTE)
    event_skip = make_event("s2", StrategyLifecycleAction.PROMOTE)

    router.process_event(event_ok)
    router.process_event(event_skip)

    notifications = router.notifications()

    assert len(notifications) == 1
    assert notifications[0].strategy_id == "s1"
    assert "PROMOTE" in notifications[0].message


def test_multiple_subscriptions_receive_notifications():
    sub1 = NotificationSubscription(
        channel=NotificationChannel.CONSOLE,
        strategy_ids={"s1"},
        actions=None,
    )
    sub2 = NotificationSubscription(
        channel=NotificationChannel.CONSOLE,
        strategy_ids=None,
        actions={StrategyLifecycleAction.DEMOTE},
    )

    router = NotificationsRouter(subscriptions=[sub1, sub2])

    router.process_event(make_event("s1", StrategyLifecycleAction.DEMOTE))

    notifications = router.notifications()

    assert len(notifications) == 2


def test_no_duplicate_notifications_for_same_event_and_subscription():
    sub = NotificationSubscription(
        channel=NotificationChannel.CONSOLE,
        strategy_ids=None,
        actions=None,
    )

    router = NotificationsRouter(subscriptions=[sub])

    event = make_event("s1", StrategyLifecycleAction.HOLD)

    router.process_event(event)
    router.process_event(event)  # replay

    notifications = router.notifications()

    assert len(notifications) == 1
