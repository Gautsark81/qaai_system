import pytest

from core.execution.squareoff.authority import ForcedSquareOffAuthority
from core.execution.squareoff.reasons import SquareOffReason
from core.safety.kill_switch import GlobalKillSwitch


def test_squareoff_cannot_be_disabled():
    ks = GlobalKillSwitch()
    authority = ForcedSquareOffAuthority(kill_switch=ks)

    ks.engage(reason="Emergency", triggered_by="system")

    intent = authority.evaluate()

    assert intent.reason == SquareOffReason.KILL_SWITCH
