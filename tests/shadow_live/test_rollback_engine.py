from datetime import datetime
from modules.shadow_live.shadow_state import ShadowLiveState
from modules.shadow_live.rollback_engine import ShadowRollbackEngine


def test_rollback_sets_killed():
    state = ShadowLiveState("s1", datetime.utcnow(), 100_000, 0, -5_000)
    rolled = ShadowRollbackEngine().rollback(state, "drawdown")

    assert rolled.killed_at is not None
