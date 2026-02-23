import pytest

from core.execution.squareoff.authority import ForcedSquareOffAuthority
from core.safety.kill_switch import GlobalKillSwitch
from core.execution.squareoff.reasons import SquareOffReason


def test_squareoff_triggers_on_global_kill_switch():
    ks = GlobalKillSwitch()
    authority = ForcedSquareOffAuthority(kill_switch=ks)

    ks.engage(reason="Risk breach", triggered_by="system")

    intent = authority.evaluate()

    assert intent is not None
    assert intent.reason == SquareOffReason.KILL_SWITCH
