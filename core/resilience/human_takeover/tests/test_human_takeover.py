from core.resilience.human_takeover.controller import HumanTakeoverController
from core.resilience.human_takeover.models import ControlAuthority


def test_initial_authority_is_system():
    ctl = HumanTakeoverController()
    assert ctl.current_authority() == ControlAuthority.SYSTEM


def test_human_takeover_switches_authority():
    ctl = HumanTakeoverController()
    event = ctl.request_takeover(reason="extreme event", evidence={})

    assert ctl.current_authority() == ControlAuthority.HUMAN
    assert event.authority == ControlAuthority.HUMAN


def test_idempotent_takeover_request():
    ctl = HumanTakeoverController()
    ctl.request_takeover(reason="first", evidence={})
    event = ctl.request_takeover(reason="second", evidence={})

    assert ctl.current_authority() == ControlAuthority.HUMAN
    assert "already" in event.reason


def test_release_returns_control_to_system():
    ctl = HumanTakeoverController()
    ctl.request_takeover(reason="incident", evidence={})
    event = ctl.release_takeover(reason="resolved", evidence={})

    assert ctl.current_authority() == ControlAuthority.SYSTEM
    assert event.authority == ControlAuthority.SYSTEM


def test_idempotent_release():
    ctl = HumanTakeoverController()
    event = ctl.release_takeover(reason="noop", evidence={})

    assert ctl.current_authority() == ControlAuthority.SYSTEM
    assert "already" in event.reason
