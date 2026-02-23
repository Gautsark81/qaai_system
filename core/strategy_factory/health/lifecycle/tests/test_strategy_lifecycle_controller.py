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


def utc_now():
    return datetime.now(timezone.utc)


def make_report(
    *,
    strategy_id: str,
    trade_count: int,
    win_rate: float,
    drawdown: float,
    last_active_days_ago: int | None,
):
    last_active_at = (
        None
        if last_active_days_ago is None
        else utc_now() - timedelta(days=last_active_days_ago)
    )

    return StrategyHealthReport(
        strategy_id=strategy_id,
        recent_returns=[0.5, -0.2],
        win_rate=win_rate,
        drawdown=drawdown,
        trade_count=trade_count,
        last_active_at=last_active_at,
    )


def test_controller_is_advisory_only():
    controller = StrategyLifecycleController(
        aggregator=StrategyHealthAggregator(reports=[])
    )

    assert controller.advisory_only is True


def test_promote_when_healthy_and_promotion_pressure():
    reports = [
        make_report(
            strategy_id="s1",
            trade_count=100,
            win_rate=0.7,
            drawdown=-2,
            last_active_days_ago=1,
        ),
        make_report(
            strategy_id="s2",
            trade_count=80,
            win_rate=0.68,
            drawdown=-3,
            last_active_days_ago=2,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)
    controller = StrategyLifecycleController(aggregator=agg)

    actions = controller.actions_by_strategy

    assert actions["s1"] == StrategyLifecycleAction.PROMOTE
    assert actions["s2"] == StrategyLifecycleAction.PROMOTE


def test_hold_when_healthy_but_no_promotion_pressure():
    reports = [
        make_report(
            strategy_id="healthy",
            trade_count=60,
            win_rate=0.65,
            drawdown=-3,
            last_active_days_ago=1,
        ),
        make_report(
            strategy_id="degraded",
            trade_count=40,
            win_rate=0.5,
            drawdown=-12,
            last_active_days_ago=2,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)
    controller = StrategyLifecycleController(aggregator=agg)

    actions = controller.actions_by_strategy

    assert actions["healthy"] == StrategyLifecycleAction.HOLD
    assert actions["degraded"] == StrategyLifecycleAction.WATCH


def test_demote_and_sunset():
    reports = [
        make_report(
            strategy_id="dying",
            trade_count=30,
            win_rate=0.45,
            drawdown=-6,
            last_active_days_ago=45,
        ),
        make_report(
            strategy_id="dead",
            trade_count=0,
            win_rate=0.0,
            drawdown=0.0,
            last_active_days_ago=None,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)
    controller = StrategyLifecycleController(aggregator=agg)

    actions = controller.actions_by_strategy

    assert actions["dying"] == StrategyLifecycleAction.DEMOTE
    assert actions["dead"] == StrategyLifecycleAction.SUNSET
