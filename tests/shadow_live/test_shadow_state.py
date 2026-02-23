from datetime import datetime
from modules.shadow_live.shadow_state import ShadowLiveState


def test_shadow_state_active():
    state = ShadowLiveState("s1", datetime.utcnow(), 100_000, 0, 0)
    assert state.is_active()
