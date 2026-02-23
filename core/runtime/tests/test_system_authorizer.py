from core.runtime.system_authorizer import (
    SystemAuthorizer,
    AuthorizationDecision,
)
from core.lifecycle.contracts.state import LifecycleState


class DummyReadinessResult:
    def __init__(self, allowed: bool, reason: str):
        self.allowed = allowed
        self.reason = reason


class DummyReadinessGate:
    def __init__(self, allowed: bool, reason: str = "OK"):
        self._result = DummyReadinessResult(allowed=allowed, reason=reason)

    def evaluate(self):
        return self._result


def test_authorizer_blocks_on_readiness_failure():
    gate = DummyReadinessGate(False, "Config invalid")
    authorizer = SystemAuthorizer(readiness_gate=gate)

    result = authorizer.authorize(
        lifecycle_state=LifecycleState.LIVE,
        execution_guard_armed=True,
    )

    assert result.decision == AuthorizationDecision.HALT
    assert "Readiness blocked" in result.reason


def test_authorizer_blocks_on_bad_lifecycle_state():
    gate = DummyReadinessGate(True)
    authorizer = SystemAuthorizer(readiness_gate=gate)

    result = authorizer.authorize(
        lifecycle_state=LifecycleState.DEGRADED,
        execution_guard_armed=True,
    )

    assert result.decision == AuthorizationDecision.HALT
    assert "Lifecycle state blocks" in result.reason


def test_authorizer_blocks_when_execution_guard_not_armed():
    gate = DummyReadinessGate(True)
    authorizer = SystemAuthorizer(readiness_gate=gate)

    result = authorizer.authorize(
        lifecycle_state=LifecycleState.LIVE,
        execution_guard_armed=False,
    )

    assert result.decision == AuthorizationDecision.HALT
    assert "Execution guard not armed" in result.reason


def test_authorizer_allows_run_when_all_clear():
    gate = DummyReadinessGate(True)
    authorizer = SystemAuthorizer(readiness_gate=gate)

    result = authorizer.authorize(
        lifecycle_state=LifecycleState.LIVE,
        execution_guard_armed=True,
    )

    assert result.decision == AuthorizationDecision.RUN
    assert result.reason == "System authorized to run"
