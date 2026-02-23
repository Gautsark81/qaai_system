from dataclasses import dataclass

from core.execution.gates.execution_permission import ExecutionPermission
from core.execution.gates.gate_chain import ExecutionGateChain


@dataclass(frozen=True)
class ExecutionGateResult:
    """
    Immutable execution admission result.
    """

    permission: ExecutionPermission


class ExecutionGateEvaluator:
    """
    Policy-free execution admission evaluator.

    - Delegates to ExecutionGateChain
    - Returns immutable result
    - NO execution logic
    """

    def __init__(self, gate_chain: ExecutionGateChain):
        self._gate_chain = gate_chain

    def evaluate(self, context) -> ExecutionGateResult:
        permission = self._gate_chain.evaluate(context)
        return ExecutionGateResult(permission=permission)
