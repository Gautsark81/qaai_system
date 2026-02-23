from domain.runtime.runtime_gate import RuntimeGate


def test_runtime_gate_blocks_execution():
    res = RuntimeGate.check_execution(
        fingerprint_valid=True,
        promotion_allowed=False,
        kill_switch_clear=True,
    )
    assert res.valid is False
