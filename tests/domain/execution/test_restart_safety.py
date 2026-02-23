from domain.execution.execution_ledger import ExecutionLedger
from domain.execution.restart_safety import RestartSafety


def test_restart_safe_with_ledger():
    assert RestartSafety.safe_to_start(ExecutionLedger()) is True
