from core.v2.control_plane.kill_matrix import evaluate_kill_matrix
from core.v2.control_plane.contracts import (
    KillAction,
    KillScope,
    KillSeverity,
    KillSignal,
)


def test_no_kill_signals_allows_execution():
    decision = evaluate_kill_matrix([])

    assert decision.allowed is True
    assert decision.action == KillAction.CONTINUE


def test_critical_kill_halts_globally():
    decision = evaluate_kill_matrix(
        [
            KillSignal(
                source="capital_guard",
                severity=KillSeverity.CRITICAL,
                action=KillAction.HALT,
                scope=KillScope.GLOBAL,
                reason="Capital breach",
            )
        ]
    )

    assert decision.allowed is False
    assert decision.action == KillAction.HALT
    assert decision.scope == KillScope.GLOBAL
    assert decision.triggered_by == "capital_guard"
