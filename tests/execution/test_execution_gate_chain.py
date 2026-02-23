from core.execution.gates.gate_chain import ExecutionGateChain
from core.execution.gates.gate_result import ExecutionGateResult
from core.execution.gates.base import ExecutionGate


class AlwaysAllowGate(ExecutionGate):
    def evaluate(self, context):
        return ExecutionGateResult(
            allowed=True,
            reasons=["allow"],
        )


class AlwaysDenyGate(ExecutionGate):
    def evaluate(self, context):
        return ExecutionGateResult(
            allowed=False,
            reasons=["deny"],
        )


def test_all_gates_pass_produces_allowed_permission():
    chain = ExecutionGateChain(
        gates=[
            AlwaysAllowGate(),
            AlwaysAllowGate(),
        ]
    )

    permission = chain.evaluate(context=None)

    assert permission.allowed is True
    assert permission.reasons == ["allow", "allow"]


def test_first_denial_blocks_execution():
    chain = ExecutionGateChain(
        gates=[
            AlwaysAllowGate(),
            AlwaysDenyGate(),
            AlwaysAllowGate(),
        ]
    )

    permission = chain.evaluate(context=None)

    assert permission.allowed is False
    assert permission.reasons == ["allow", "deny"]


def test_empty_gate_chain_allows_execution():
    chain = ExecutionGateChain(gates=[])

    permission = chain.evaluate(context=None)

    assert permission.allowed is True
    assert permission.reasons == []
