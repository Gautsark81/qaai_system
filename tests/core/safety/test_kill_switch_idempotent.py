from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope


def test_kill_switch_is_idempotent():
    ks = KillSwitch()

    ks.trip(KillScope.GLOBAL, reason="first")
    ks.trip(KillScope.GLOBAL, reason="second")  # should not error

    assert ks.is_tripped(KillScope.GLOBAL)
