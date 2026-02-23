from datetime import datetime, timedelta, timezone

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)
from core.strategy_factory.health.reports.strategy_health_aggregator import (
    StrategyHealthAggregator,
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


def test_aggregator_is_advisory_only():
    agg = StrategyHealthAggregator(reports=[])

    assert agg.advisory_only is True


def test_empty_aggregation_is_healthy_and_zeroed():
    agg = StrategyHealthAggregator(reports=[])

    assert agg.total_strategies == 0
    assert agg.overall_status == StrategyHealthStatus.HEALTHY
    assert agg.status_counts == {
        StrategyHealthStatus.HEALTHY: 0,
        StrategyHealthStatus.DEGRADED: 0,
        StrategyHealthStatus.DYING: 0,
        StrategyHealthStatus.DEAD: 0,
    }


def test_worst_status_dominance_dead():
    reports = [
        make_report(
            strategy_id="s1",
            trade_count=50,
            win_rate=0.65,
            drawdown=-3,
            last_active_days_ago=1,
        ),
        make_report(
            strategy_id="s2",
            trade_count=0,
            win_rate=0.0,
            drawdown=0.0,
            last_active_days_ago=None,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)

    assert agg.overall_status == StrategyHealthStatus.DEAD
    assert agg.dead_strategies == ["s2"]


def test_worst_status_dominance_dying():
    reports = [
        make_report(
            strategy_id="s1",
            trade_count=40,
            win_rate=0.6,
            drawdown=-4,
            last_active_days_ago=1,
        ),
        make_report(
            strategy_id="s2",
            trade_count=20,
            win_rate=0.45,
            drawdown=-6,
            last_active_days_ago=45,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)

    assert agg.overall_status == StrategyHealthStatus.DYING
    assert agg.dying_strategies == ["s2"]


def test_promotion_and_demotion_pressure():
    reports = [
        make_report(
            strategy_id="healthy_1",
            trade_count=80,
            win_rate=0.7,
            drawdown=-2,
            last_active_days_ago=1,
        ),
        make_report(
            strategy_id="healthy_2",
            trade_count=90,
            win_rate=0.68,
            drawdown=-1,
            last_active_days_ago=2,
        ),
        make_report(
            strategy_id="degraded_1",
            trade_count=50,
            win_rate=0.5,
            drawdown=-12,
            last_active_days_ago=3,
        ),
    ]

    agg = StrategyHealthAggregator(reports=reports)

    assert agg.promotion_pressure is True
    assert agg.demotion_pressure is True
