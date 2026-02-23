# tests/execution/test_execution_plan_builder.py

from datetime import datetime

from modules.execution.plan_builder import build_execution_plan_legacy
from modules.strategies.intent import StrategyIntent


def make_intent(confidence=0.6):
    return StrategyIntent(
        strategy_id="s1",
        symbol="NIFTY",
        side="BUY",
        confidence=confidence,
        features_used=["ema_fast", "ema_slow"],
        timestamp=datetime(2024, 1, 1),
    )


def test_plan_created_for_valid_intent():
    intent = make_intent(0.7)

    plan = build_execution_plan_legacy(
        intent=intent,
        max_quantity=5,
    )

    assert plan is not None
    assert plan.quantity == 5
    assert plan.side == "BUY"
    assert plan.order_type == "MARKET"


def test_low_confidence_blocks_plan():
    intent = make_intent(0.4)

    plan = build_execution_plan_legacy(
        intent=intent,
        max_quantity=5,
    )

    assert plan is None


def test_plan_id_deterministic():
    intent = make_intent(0.8)

    p1 = build_execution_plan_legacy(
        intent=intent,
        max_quantity=1,
    )
    p2 = build_execution_plan_legacy(
        intent=intent,
        max_quantity=1,
    )

    assert p1.plan_id == p2.plan_id
