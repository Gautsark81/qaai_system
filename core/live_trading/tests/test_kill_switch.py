import pytest
from core.live_trading.kill_switch import KillSwitch


def test_kill_switch_blocks_execution():
    ks = KillSwitch()
    ks.arm()

    with pytest.raises(RuntimeError):
        ks.assert_not_armed()


def test_kill_switch_disarm_allows_execution():
    ks = KillSwitch()
    ks.disarm()

    ks.assert_not_armed()  # no error
