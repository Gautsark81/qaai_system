from domain.validation.execution_gate import ExecutionGate


def test_execution_blocked_when_any_gate_fails():
    res = ExecutionGate.allow_execution(
        fingerprint_valid=True,
        promotion_allowed=False,
        kill_switch_clear=True,
    )
    assert res.valid is False
    assert "Promotion rules blocked execution" in res.errors[0]
