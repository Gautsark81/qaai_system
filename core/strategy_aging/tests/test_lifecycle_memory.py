from datetime import datetime
from core.strategy_aging.memory import build_lifecycle_memory
from core.strategy_aging.models import StrategyLifecycleState


def test_lifecycle_memory_appends_state():
    now = datetime.utcnow()

    memory = build_lifecycle_memory(
        strategy_id="s1",
        prior_states=(StrategyLifecycleState.YOUNG,),
        new_state=StrategyLifecycleState.MATURE,
        first_seen=now,
        now=now,
    )

    assert memory.historical_states == (
        StrategyLifecycleState.YOUNG,
        StrategyLifecycleState.MATURE,
    )
