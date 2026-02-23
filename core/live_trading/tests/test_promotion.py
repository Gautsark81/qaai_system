from core.live_trading.promotion import (
    CanaryPromotionEngine,
    CanaryPolicy,
)
from core.live_trading.status import ExecutionStatus
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote


def _live_strategy():
    registry = StrategyRegistry()

    spec = StrategySpec(
        name="test",
        alpha_stream="alpha_canary",
        timeframe="5m",
        universe=["NIFTY"],
        params={"x": 1},
    )

    record = registry.register(spec)

    promote(record, "BACKTESTED")
    promote(record, "PAPER")
    promote(record, "LIVE")

    return registry, record


def test_strategy_downgraded_on_high_divergence():
    registry, record = _live_strategy()

    engine = CanaryPromotionEngine(
        registry=registry,
        policy=CanaryPolicy(
            max_divergence=0.5,
            max_slippage=1.0,
        ),
    )

    decision = engine.evaluate(
        dna=record.dna,
        divergence_score=1.2,
        avg_slippage=0.1,
    )

    assert decision == "DOWNGRADE"
    assert record.execution_status == ExecutionStatus.FROZEN
    assert record.state == "LIVE"   # lifecycle intact


def test_strategy_frozen_on_high_slippage():
    registry, record = _live_strategy()

    engine = CanaryPromotionEngine(
        registry=registry,
        policy=CanaryPolicy(
            max_divergence=1.0,
            max_slippage=0.2,
        ),
    )

    decision = engine.evaluate(
        dna=record.dna,
        divergence_score=0.1,
        avg_slippage=0.5,
    )

    assert decision == "FREEZE"
    assert record.execution_status == ExecutionStatus.FROZEN
    assert record.state == "LIVE"


def test_strategy_continues_when_stable():
    registry, record = _live_strategy()

    engine = CanaryPromotionEngine(
        registry=registry,
        policy=CanaryPolicy(
            max_divergence=1.0,
            max_slippage=1.0,
        ),
    )

    decision = engine.evaluate(
        dna=record.dna,
        divergence_score=0.1,
        avg_slippage=0.05,
    )

    assert decision == "CONTINUE"
    assert record.execution_status == ExecutionStatus.ACTIVE
    assert record.state == "LIVE"
