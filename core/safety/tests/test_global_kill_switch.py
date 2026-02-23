import pytest
from datetime import datetime, timezone

from core.safety.kill_switch import (
    GlobalKillSwitch,
    KillSwitchState,
    KillSwitchEvent,
)


def test_kill_switch_initially_disengaged():
    ks = GlobalKillSwitch()

    assert ks.state == KillSwitchState.DISENGAGED
    assert ks.is_active is False


def test_kill_switch_engages_and_blocks():
    ks = GlobalKillSwitch()

    event = ks.engage(
        reason="Manual operator halt",
        triggered_by="operator",
    )

    assert ks.state == KillSwitchState.ENGAGED
    assert ks.is_active is True
    assert isinstance(event, KillSwitchEvent)
    assert event.reason == "Manual operator halt"


def test_kill_switch_is_latched():
    ks = GlobalKillSwitch()

    ks.engage(reason="Risk breach", triggered_by="system")

    with pytest.raises(RuntimeError):
        ks.engage(reason="Second trigger", triggered_by="system")


def test_kill_switch_cannot_be_auto_reset():
    ks = GlobalKillSwitch()
    ks.engage(reason="Emergency", triggered_by="operator")

    with pytest.raises(RuntimeError):
        ks.reset(triggered_by="system")


def test_kill_switch_requires_explicit_operator_reset():
    ks = GlobalKillSwitch()
    ks.engage(reason="Emergency", triggered_by="operator")

    reset_event = ks.reset(triggered_by="operator")

    assert ks.state == KillSwitchState.DISENGAGED
    assert reset_event.triggered_by == "operator"


def test_kill_switch_emits_auditable_events():
    ks = GlobalKillSwitch()

    engage_event = ks.engage(
        reason="Manual halt",
        triggered_by="operator",
    )

    reset_event = ks.reset(triggered_by="operator")

    assert engage_event.timestamp.tzinfo == timezone.utc
    assert reset_event.timestamp.tzinfo == timezone.utc


def test_kill_switch_is_deterministic():
    ks = GlobalKillSwitch()

    ks.engage(reason="Test", triggered_by="operator")

    assert ks.is_active is True
    assert ks.is_active is True  # repeatable, no mutation
