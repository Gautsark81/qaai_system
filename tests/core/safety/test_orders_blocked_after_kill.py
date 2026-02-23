import pytest

from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope


def test_orders_blocked_after_global_kill():
    ks = KillSwitch()
    ks.trip(KillScope.GLOBAL, reason="risk breach")

    with pytest.raises(RuntimeError):
        ks.assert_can_trade()
