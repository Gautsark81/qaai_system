from domain.runtime.kill_switch_gate import KillSwitchGate


def test_kill_switch_blocks_when_not_acknowledged():
    res = KillSwitchGate.allow_execution(
        armed=True,
        acknowledged=False,
    )
    assert res.valid is False
