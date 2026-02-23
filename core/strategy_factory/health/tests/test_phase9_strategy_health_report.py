from datetime import datetime, timezone

import pytest

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)


def test_strategy_health_report_constructs_and_is_advisory():
    report = StrategyHealthReport(
        strategy_id="STRAT_001",
        recent_returns=[0.02, -0.01, 0.03],
        win_rate=0.6,
        drawdown=-0.05,
        trade_count=120,
        last_active_at=datetime.now(timezone.utc),
    )

    assert report.strategy_id == "STRAT_001"
    assert report.advisory_only is True
    assert report.status in StrategyHealthStatus
    assert isinstance(report.health_score, int)
    assert isinstance(report.reasons, list)


def test_strategy_health_report_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError):
        StrategyHealthReport(
            strategy_id="STRAT_BAD",
            recent_returns=[0.01],
            win_rate=0.5,
            drawdown=-0.01,
            trade_count=10,
            last_active_at=datetime.utcnow().replace(tzinfo=None),
        )
