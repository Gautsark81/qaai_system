from datetime import datetime

import pytest

from core.system.readiness import (
    SystemReadinessGate,
    SystemMode,
    ReadinessReason,
)


def _base_kwargs(**overrides):
    base = dict(
        now=datetime.utcnow(),
        bootstrap_complete=True,
        governance_approved=True,
        capital_ready=True,
        execution_guard_clear=True,
        kill_switch_active=False,
        manual_halt=False,
        requested_mode=SystemMode.PAPER,
    )
    base.update(overrides)
    return base


def test_system_ready_for_paper():
    gate = SystemReadinessGate()

    snap = gate.evaluate(**_base_kwargs())

    assert snap.is_ready is True
    assert snap.mode == SystemMode.PAPER
    assert snap.blocking_reasons == {ReadinessReason.OK}


def test_live_requires_governance():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(
            requested_mode=SystemMode.LIVE,
            governance_approved=False,
        )
    )

    assert snap.is_ready is False
    assert snap.mode == SystemMode.HALTED
    assert ReadinessReason.GOVERNANCE_NOT_APPROVED in snap.blocking_reasons


def test_kill_switch_dominates_everything():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(
            kill_switch_active=True,
            requested_mode=SystemMode.LIVE,
        )
    )

    assert snap.is_ready is False
    assert snap.mode == SystemMode.HALTED
    assert ReadinessReason.KILL_SWITCH_ACTIVE in snap.blocking_reasons


def test_bootstrap_incomplete_blocks_run():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(bootstrap_complete=False)
    )

    assert snap.is_ready is False
    assert ReadinessReason.BOOTSTRAP_INCOMPLETE in snap.blocking_reasons


def test_execution_guard_blocks_run():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(execution_guard_clear=False)
    )

    assert snap.is_ready is False
    assert ReadinessReason.EXECUTION_GUARD_BLOCKED in snap.blocking_reasons


def test_capital_not_ready_blocks_run():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(capital_ready=False)
    )

    assert snap.is_ready is False
    assert ReadinessReason.CAPITAL_NOT_READY in snap.blocking_reasons


def test_manual_halt_blocks_even_if_everything_else_ok():
    gate = SystemReadinessGate()

    snap = gate.evaluate(
        **_base_kwargs(manual_halt=True)
    )

    assert snap.is_ready is False
    assert ReadinessReason.MANUAL_HALT in snap.blocking_reasons
