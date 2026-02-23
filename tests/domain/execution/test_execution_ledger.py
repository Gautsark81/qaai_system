from domain.execution.execution_ledger import ExecutionLedger


def test_ledger_records_and_reads():
    l = ExecutionLedger()
    l.record("i1", "b1")
    assert l.exists("i1")
    assert l.get("i1") == "b1"
