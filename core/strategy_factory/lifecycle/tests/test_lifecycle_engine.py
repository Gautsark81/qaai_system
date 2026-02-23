from core.strategy_factory.lifecycle.lifecycle_engine import LifecycleEngine
from core.strategy_factory.lifecycle.state_machine import LifecycleState


def test_freeze_on_fragility():
    engine = LifecycleEngine()
    event = engine.decide(
        strategy_dna="x",
        current_state=LifecycleState.PAPER,
        fragility=0.9,
    )
    assert event.to_state == LifecycleState.FROZEN
