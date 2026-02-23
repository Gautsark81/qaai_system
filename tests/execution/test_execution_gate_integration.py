import pytest

from core.execution.engine_execution_gate import (
    ExecutionGateEvaluator,
    ExecutionGateResult,
)
from core.execution.execution_entry_gate import ExecutionEntryGate
from core.execution.gates.execution_permission import ExecutionPermission


class DummyGateChainAllow:
    def evaluate(self, context):
        return ExecutionPermission(
            allowed=True,
            reasons=[],
        )


class DummyGateChainDeny:
    def evaluate(self, context):
        return ExecutionPermission(
            allowed=False,
            reasons=["blocked"],
        )


def test_execution_gate_allows_execution():
    evaluator = ExecutionGateEvaluator(DummyGateChainAllow())

    result = evaluator.evaluate(context={})

    assert isinstance(result, ExecutionGateResult)
    assert result.permission.allowed is True


def test_execution_gate_blocks_execution():
    evaluator = ExecutionGateEvaluator(DummyGateChainDeny())

    result = evaluator.evaluate(context={})

    assert result.permission.allowed is False
    assert "blocked" in result.permission.reasons


def test_execution_entry_gate_allows_when_permitted():
    result = ExecutionGateResult(
        permission=ExecutionPermission(
            allowed=True,
            reasons=[],
        )
    )

    ExecutionEntryGate.ensure_allowed(result)


def test_execution_entry_gate_blocks_when_denied():
    result = ExecutionGateResult(
        permission=ExecutionPermission(
            allowed=False,
            reasons=["risk"],
        )
    )

    with pytest.raises(PermissionError):
        ExecutionEntryGate.ensure_allowed(result)
