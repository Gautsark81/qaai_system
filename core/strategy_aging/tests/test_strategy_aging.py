from datetime import datetime, timedelta
from core.strategy_aging.aging import build_aging_signal
from core.strategy_aging.models import StrategyLifecycleState


def test_strategy_aging_state_transitions():
    now = datetime.utcnow()
    first_seen = now - timedelta(days=200)

    signal = build_aging_signal(
        strategy_id="s1",
        first_seen=first_seen,
        last_activity=now - timedelta(days=190),
        now=now,
        decay_score=0.8,
    )

    assert signal.state == StrategyLifecycleState.ZOMBIE
