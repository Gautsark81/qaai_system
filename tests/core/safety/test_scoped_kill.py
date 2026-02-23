from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope


def test_scoped_kill_does_not_affect_others():
    ks = KillSwitch()

    ks.trip(KillScope.STRATEGY, key="strat-A")

    assert ks.is_tripped(KillScope.STRATEGY, key="strat-A")
    assert not ks.is_tripped(KillScope.STRATEGY, key="strat-B")
    assert not ks.is_tripped(KillScope.GLOBAL)
