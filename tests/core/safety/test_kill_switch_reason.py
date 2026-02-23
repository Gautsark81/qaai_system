from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope


def test_kill_switch_reason_preserved():
    ks = KillSwitch()
    ks.trip(KillScope.GLOBAL, reason="broker down")

    assert ks.reason(KillScope.GLOBAL) == "broker down"
