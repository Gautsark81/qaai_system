from domain.execution.execution_intent import ExecutionIntent


def test_execution_intent_id_deterministic():
    i1 = ExecutionIntent("S1", "NIFTY", "BUY", 1, "MARKET", None, {})
    i2 = ExecutionIntent("S1", "NIFTY", "BUY", 1, "MARKET", None, {})
    assert i1.intent_id() == i2.intent_id()
