from datetime import datetime, timedelta, timezone

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)
from core.strategy_factory.health.reports.strategy_health_aggregator import (
    StrategyHealthAggregator,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
    StrategyLifecycleController,
)
from core.strategy_factory.health.lifecycle.lifecycle_audit_log import (
    LifecycleAuditLog,
)
from core.strategy_factory.health.notifications.notifications_router import (
    NotificationChannel,
    NotificationSubscription,
    NotificationsRouter,
)
from core.strategy_factory.health.dashboard.dashboard_view_models import (
    StrategyRowVM,
    PortfolioSummaryVM,
    NotificationFeedItemVM,
)


def utc_now():
    return datetime.now(timezone.utc)


def make_report(strategy_id, trade_count, win_rate, drawdown, days_ago):
    last_active_at = (
        None if days_ago is None else utc_now() - timedelta(days=days_ago)
    )
    return StrategyHealthReport(
        strategy_id=strategy_id,
        recent_returns=[0.3, -0.1],
        win_rate=win_rate,
        drawdown=drawdown,
        trade_count=trade_count,
        last_active_at=last_active_at,
    )


def test_strategy_row_vm_is_read_only_and_deterministic():
    report = make_report("s1", 80, 0.7, -2, 1)

    agg = StrategyHealthAggregator(reports=[report])
    controller = StrategyLifecycleController(aggregator=agg)

    row = StrategyRowVM.from_domain(
        report=report,
        lifecycle_action=controller.actions_by_strategy["s1"],
        last_event_at=None,
    )

    assert row.strategy_id == "s1"
    assert row.health_status == StrategyHealthStatus.HEALTHY
    assert row.lifecycle_action == StrategyLifecycleAction.PROMOTE
    assert row.health_score == report.health_score
    assert isinstance(row.reasons, list)


def test_portfolio_summary_vm():
    reports = [
        make_report("s1", 80, 0.7, -2, 1),
        make_report("s2", 40, 0.5, -12, 2),
    ]

    agg = StrategyHealthAggregator(reports=reports)

    summary = PortfolioSummaryVM.from_aggregator(agg)

    assert summary.total_strategies == 2
    assert summary.counts[StrategyHealthStatus.HEALTHY] == 1
    assert summary.counts[StrategyHealthStatus.DEGRADED] == 1
    assert summary.promotion_pressure is True
    assert summary.demotion_pressure is True


def test_notification_feed_item_vm():
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

    notifications = router.notifications()
    vm = NotificationFeedItemVM.from_notification(notifications[0])

    assert vm.strategy_id == "s1"
    assert vm.action == StrategyLifecycleAction.HOLD
    assert "s1" in vm.message
