from domain.validation.kill_switch_rules import KillSwitchRules


def test_armed_kill_switch_blocks():
    res = KillSwitchRules.validate(armed=True, acknowledged=False)
    assert res.valid is False
