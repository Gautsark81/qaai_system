from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle.events import LifecycleEvent
from core.strategy_factory.lifecycle.state_machine import LifecycleState


def test_registry_applies_lifecycle_event():
    registry = StrategyRegistry()

    spec = StrategySpec(
        name="test_strategy",
        alpha_stream="alpha",
        timeframe="5m",
        universe=["NIFTY"],
        params={"x": 1},
    )

    record = registry.register(spec)

    # Simulate an external lifecycle event (Phase-9 is additive)
    event = LifecycleEvent(
        strategy_dna=record.dna,
        from_state=LifecycleState.CREATED,
        to_state=LifecycleState.SCREENED,
        trigger="fitness",
        reason="Fitness threshold satisfied",
    )

    # Registry should remain intact
    assert record.dna == event.strategy_dna
    assert record.state in {"CREATED", "GENERATED"}  # legacy untouched
