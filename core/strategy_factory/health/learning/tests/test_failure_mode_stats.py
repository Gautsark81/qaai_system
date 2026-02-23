from core.strategy_factory.health.learning.failure_mode_stats import (
    FailureModeStats,
)
from core.strategy_factory.health.death_reason import DeathReason


def test_failure_mode_stats_basic():
    stats = FailureModeStats(
        total_deaths=5,
        reason_counts={
            DeathReason.MAX_DRAWDOWN: 3,
            DeathReason.SSR_FAILURE: 2,
        },
    )

    assert stats.total_deaths == 5
    assert stats.reason_counts[DeathReason.MAX_DRAWDOWN] == 3
    assert stats.reason_ratios[DeathReason.MAX_DRAWDOWN] == 0.6
    assert stats.reason_ratios[DeathReason.SSR_FAILURE] == 0.4


def test_failure_mode_stats_zero_deaths():
    stats = FailureModeStats(
        total_deaths=0,
        reason_counts={},
    )

    assert stats.reason_ratios == {}


def test_failure_mode_stats_is_immutable():
    stats = FailureModeStats(
        total_deaths=1,
        reason_counts={DeathReason.OPERATOR_KILL: 1},
    )

    try:
        stats.total_deaths = 99
        assert False, "FailureModeStats must be immutable"
    except AttributeError:
        pass


def test_failure_mode_stats_repr():
    stats = FailureModeStats(
        total_deaths=2,
        reason_counts={DeathReason.SYSTEM_GUARDRAIL: 2},
    )

    text = repr(stats)
    assert "FailureModeStats" in text
    assert "total_deaths=2" in text
