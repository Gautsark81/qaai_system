from datetime import datetime, timedelta, timezone

import pytest

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)


def utc_now():
    return datetime.now(timezone.utc)


def test_strategy_health_report_is_advisory_only():
    report = StrategyHealthReport(
        strategy_id="strat_1",
        recent_returns=[1.2, -0.4, 0.8],
        win_rate=0.55,
        drawdown=-5.0,
        trade_count=40,
        last_active_at=utc_now(),
    )

    assert report.advisory_only is True


def test_healthy_strategy():
    report = StrategyHealthReport(
        strategy_id="healthy_strat",
        recent_returns=[1.0, 0.5, 0.8, 1.2],
        win_rate=0.65,
        drawdown=-3.0,
        trade_count=60,
        last_active_at=utc_now(),
    )

    assert report.status == StrategyHealthStatus.HEALTHY
    assert report.health_score > 70
    assert any("healthy" in r.lower() for r in report.reasons)


def test_degraded_strategy_due_to_drawdown():
    report = StrategyHealthReport(
        strategy_id="dd_strat",
        recent_returns=[-1.0, -0.5, 0.2],
        win_rate=0.45,
        drawdown=-18.0,
        trade_count=50,
        last_active_at=utc_now(),
    )

    assert report.status == StrategyHealthStatus.DEGRADED
    assert report.health_score < 70
    assert any("drawdown" in r.lower() for r in report.reasons)


def test_dying_strategy_due_to_low_activity():
    report = StrategyHealthReport(
        strategy_id="inactive_strat",
        recent_returns=[0.2, -0.1],
        win_rate=0.40,
        drawdown=-8.0,
        trade_count=12,
        last_active_at=utc_now() - timedelta(days=45),
    )

    assert report.status == StrategyHealthStatus.DYING
    assert any("inactive" in r.lower() for r in report.reasons)


def test_dead_strategy_due_to_zero_trades():
    report = StrategyHealthReport(
        strategy_id="dead_strat",
        recent_returns=[],
        win_rate=0.0,
        drawdown=0.0,
        trade_count=0,
        last_active_at=None,
    )

    assert report.status == StrategyHealthStatus.DEAD
    assert report.health_score == 0
    assert any("no trades" in r.lower() for r in report.reasons)
