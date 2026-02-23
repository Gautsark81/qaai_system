from domain.runtime.execution_entry_gate import ExecutionEntryGate


def test_execution_entry_gate_allows_only_when_all_clear():
    res = ExecutionEntryGate.allow(
        fingerprint_valid=True,
        promotion_allowed=True,
        kill_switch_clear=True,
    )
    assert res.valid is True
