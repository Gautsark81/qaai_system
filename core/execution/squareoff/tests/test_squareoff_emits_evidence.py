from core.execution.squareoff.authority import ForcedSquareOffAuthority
from core.safety.kill_switch import GlobalKillSwitch


def test_squareoff_emits_audit_event():
    ks = GlobalKillSwitch()
    authority = ForcedSquareOffAuthority(kill_switch=ks)

    ks.engage(reason="Emergency", triggered_by="system")

    intent = authority.evaluate()

    assert intent.audit_id is not None
    assert intent.timestamp is not None
