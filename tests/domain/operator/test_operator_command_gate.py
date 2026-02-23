from domain.operator.operator_command_gate import OperatorCommandGate


def test_operator_command_gate():
    assert OperatorCommandGate.allow("KILL") is True
    assert OperatorCommandGate.allow("TRADE") is False
