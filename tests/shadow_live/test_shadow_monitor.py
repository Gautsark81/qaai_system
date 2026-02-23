from datetime import datetime
from modules.shadow_live.shadow_monitor import ShadowLiveMonitor
from modules.shadow_live.shadow_state import ShadowLiveState
from modules.shadow_live.health_policy import ShadowHealthPolicy


def test_shadow_monitor_kills():
    policy = ShadowHealthPolicy(0.05, 0.5, 10_000)
    monitor = ShadowLiveMonitor(policy)

    state = ShadowLiveState(
        "s1", datetime.utcnow(), 100_000, 100_000, 90_000
    )

    assert monitor.should_kill(state, ssr=0.9)
