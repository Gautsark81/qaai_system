from core.execution.squareoff.authority import ForcedSquareOffAuthority
from core.execution.squareoff.reasons import SquareOffReason
from core.safety.kill_switch import GlobalKillSwitch


def test_squareoff_is_idempotent():
    ks = GlobalKillSwitch()
    authority = ForcedSquareOffAuthority(kill_switch=ks)

    ks.engage(reason="Emergency", triggered_by="system")

    intent1 = authority.evaluate()
    intent2 = authority.evaluate()

    assert intent1 == intent2
