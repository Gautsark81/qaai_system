import pytest
from datetime import datetime, timedelta, timezone

from core.safety.broker_time_drift import (
    BrokerTimeDriftGuard,
    TimeDriftViolation,
)

from core.market_clock.nse_clock import NSEMarketClock
from core.safety.kill_switch import GlobalKillSwitch


UTC = timezone.utc


def _dt(h, m, s):
    return datetime(2026, 1, 27, h, m, s, tzinfo=UTC)


def test_no_drift_when_times_match():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 0))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    guard.assert_safe(broker_time=_dt(9, 20, 0))

    assert ks.is_active is False


def test_small_drift_within_threshold_allowed():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 0))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    guard.assert_safe(broker_time=_dt(9, 20, 1))

    assert ks.is_active is False


def test_positive_drift_triggers_kill_switch():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 0))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    with pytest.raises(TimeDriftViolation):
        guard.assert_safe(broker_time=_dt(9, 20, 5))

    assert ks.is_active is True


def test_negative_drift_triggers_kill_switch():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 5))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    with pytest.raises(TimeDriftViolation):
        guard.assert_safe(broker_time=_dt(9, 20, 0))

    assert ks.is_active is True


def test_violation_is_latched():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 0))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    with pytest.raises(TimeDriftViolation):
        guard.assert_safe(broker_time=_dt(9, 20, 10))

    with pytest.raises(RuntimeError):
        guard.assert_safe(broker_time=_dt(9, 20, 0))


def test_guard_is_deterministic():
    ks = GlobalKillSwitch()
    clock = NSEMarketClock.for_test_time(_dt(9, 20, 0))

    guard = BrokerTimeDriftGuard(
        market_clock=clock,
        kill_switch=ks,
        max_drift_seconds=2,
    )

    with pytest.raises(TimeDriftViolation):
        guard.assert_safe(broker_time=_dt(9, 20, 5))

    assert ks.is_active is True
    assert ks.is_active is True  # repeatable
