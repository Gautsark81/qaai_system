from domain.execution.execution_intent import ExecutionIntent
from domain.execution.execution_ledger import ExecutionLedger
from domain.execution.safe_executor import SafeExecutor


def test_safe_executor_exactly_once():
    ledger = ExecutionLedger()
    execu = SafeExecutor(ledger)

    intent = ExecutionIntent("S1", "NIFTY", "BUY", 1, "MARKET", None, {})

    calls = {"n": 0}

    def submit(_):
        calls["n"] += 1
        return "OID1"

    o1 = execu.submit(intent, submit)
    o2 = execu.submit(intent, submit)

    assert o1 == o2
    assert calls["n"] == 1
