from core.v2.control_plane.kill_matrix import evaluate_kill_matrix
from core.v2.control_plane.contracts import (
    KillAction,
    KillScope,
    KillSeverity,
    KillSignal,
)


def test_higher_severity_overrides_lower():
    decision = evaluate_kill_matrix(
        [
            KillSignal(
                source="regime_engine",
                severity=KillSeverity.HIGH,
                action=KillAction.THROTTLE,
                scope=KillScope.STRATEGY,
                reason="Regime unstable",
            ),
            KillSignal(
                source="operator",
                severity=KillSeverity.CRITICAL,
                action=KillAction.HALT,
                scope=KillScope.GLOBAL,
                reason="Manual kill",
            ),
        ]
    )

    assert decision.allowed is False
    assert decision.action == KillAction.HALT
    assert decision.triggered_by == "operator"


def test_throttle_allowed_when_no_halt():
    decision = evaluate_kill_matrix(
        [
            KillSignal(
                source="alpha_decay",
                severity=KillSeverity.HIGH,
                action=KillAction.THROTTLE,
                scope=KillScope.STRATEGY,
                reason="Alpha decay detected",
            )
        ]
    )

    assert decision.allowed is True
    assert decision.action == KillAction.THROTTLE
