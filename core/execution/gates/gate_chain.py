from typing import Iterable, List

from core.execution.gates.execution_permission import ExecutionPermission
from core.execution.gates.gate_result import ExecutionGateResult
from core.execution.gates.base import ExecutionGate


class ExecutionGateChain:
    """
    Deterministic, policy-free execution gate evaluator.

    Responsibilities:
    - Execute gates in order
    - Preserve first-failure dominance
    - Aggregate reasons
    - Emit a single ExecutionPermission

    This class:
    - Does NOT decide policy
    - Does NOT inspect strategy, capital, lifecycle, or risk semantics
    """

    def __init__(self, gates: Iterable[ExecutionGate]):
        self._gates = list(gates)

    def evaluate(self, context) -> ExecutionPermission:
        results: List[ExecutionGateResult] = []

        for gate in self._gates:
            result = gate.evaluate(context)
            results.append(result)

            if not result.allowed:
                return ExecutionPermission.denied_permission(
                    reasons=[r for r in self._flatten(results)]
                )

        return ExecutionPermission.allowed_permission(
            reasons=[r for r in self._flatten(results)]
        )

    @staticmethod
    def _flatten(results: List[ExecutionGateResult]) -> List[str]:
        reasons: List[str] = []
        for result in results:
            reasons.extend(result.reasons)
        return reasons
