import json
from datetime import datetime, timedelta, timezone

from core.strategy_factory.health.strategy_health_report import StrategyHealthReport
from core.strategy_factory.health.reports.strategy_health_aggregator import (
    StrategyHealthAggregator,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleController,
    StrategyLifecycleAction,
)
from core.strategy_factory.health.lifecycle.lifecycle_audit_log import (
    LifecycleAuditLog,
)
from core.strategy_factory.health.notifications.notifications_router import (
    NotificationsRouter,
    NotificationSubscription,
    NotificationChannel,
)
from core.strategy_factory.health.dashboard.dashboard_view_models import (
    StrategyRowVM,
    PortfolioSummaryVM,
    NotificationFeedItemVM,
)
from core.strategy_factory.health.api.dashboard_snapshot import (
    DashboardSnapshot,
)


def utc_now():
    return datetime.now(timezone.utc)


def make_report(strategy_id, trade_count, win_rate, drawdown, days_ago):
    last_active_at = (
        None if days_ago is None else utc_now() - timedelta(days=days_ago)
    )
    return StrategyHealthReport(
        strategy_id=strategy_id,
        recent_returns=[0.2, -0.1],
        win_rate=win_rate,
        drawdown=drawdown,
        trade_count=trade_count,
        last_active_at=last_active_at,
    )


def test_dashboard_snapshot_serialization_roundtrip():
    reports = [
        make_report("s1", 80, 0.7, -2, 1),
        make_report("s2", 40, 0.5, -12, 2),
    ]

    agg = StrategyHealthAggregator(reports=reports)
    controller = StrategyLifecycleController(aggregator=agg)

    rows = [
        StrategyRowVM.from_domain(
            report=r,
            lifecycle_action=controller.actions_by_strategy[r.strategy_id],
            last_event_at=None,
        )
        for r in reports
    ]

    summary = PortfolioSummaryVM.from_aggregator(agg)

    log = LifecycleAuditLog()
    log.record(
        strategy_id="s1",
        previous_action=None,
        current_action=StrategyLifecycleAction.HOLD,
        reasons=["initial"],
        timestamp=utc_now(),
    )

    router = NotificationsRouter(
        subscriptions=[
            NotificationSubscription(
                channel=NotificationChannel.CONSOLE,
                strategy_ids=None,
                actions=None,
            )
        ]
    )

    for event in log.all_events():
        router.process_event(event)

    notifications = [
        NotificationFeedItemVM.from_notification(n)
        for n in router.notifications()
    ]

    snapshot = DashboardSnapshot(
        portfolio_summary=summary,
        strategy_rows=rows,
        notifications=notifications,
        as_of=utc_now(),
    )

    payload = snapshot.to_dict()
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert decoded["portfolio_summary"]["total_strategies"] == 2
    assert len(decoded["strategy_rows"]) == 2
    assert decoded["notifications"][0]["strategy_id"] == "s1"
