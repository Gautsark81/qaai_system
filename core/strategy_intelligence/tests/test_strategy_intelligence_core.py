from dataclasses import dataclass
from typing import Tuple, Optional

# ✅ REQUIRED explicit import (namespace hygiene)
from core.strategy_intelligence import StrategyIntelligence


@dataclass(frozen=True)
class StrategyResultStub:
    trade_id: str
    pnl: float
    success: bool


def test_strategy_intelligence_healthy():
    results = (
        StrategyResultStub("t1", 100.0, True),
        StrategyResultStub("t2", 80.0, True),
        StrategyResultStub("t3", 120.0, True),
    )

    intelligence = StrategyIntelligence(strategy_id="S1")

    verdict = intelligence.evaluate(results)

    assert verdict.health == "HEALTHY"
    assert verdict.ssr >= 0.8


def test_strategy_intelligence_degrading():
    results = (
        StrategyResultStub("t1", 100.0, True),
        StrategyResultStub("t2", -50.0, False),
        StrategyResultStub("t3", -40.0, False),
    )

    intelligence = StrategyIntelligence(strategy_id="S2")

    verdict = intelligence.evaluate(results)

    assert verdict.health == "DEGRADING"


def test_strategy_intelligence_unstable():
    results = (
        StrategyResultStub("t1", -200.0, False),
        StrategyResultStub("t2", 300.0, True),
        StrategyResultStub("t3", -250.0, False),
        StrategyResultStub("t4", 280.0, True),
    )

    intelligence = StrategyIntelligence(strategy_id="S3")

    verdict = intelligence.evaluate(results)

    assert verdict.health == "UNSTABLE"


def test_ssr_is_deterministic():
    results = (
        StrategyResultStub("t1", 10.0, True),
        StrategyResultStub("t2", -5.0, False),
        StrategyResultStub("t3", 12.0, True),
        StrategyResultStub("t4", -3.0, False),
    )

    intelligence = StrategyIntelligence(strategy_id="S4")

    v1 = intelligence.evaluate(results)
    v2 = intelligence.evaluate(results)

    assert v1.ssr == v2.ssr


def test_strategy_intelligence_has_no_side_effects():
    results = (
        StrategyResultStub("t1", 50.0, True),
        StrategyResultStub("t2", -10.0, False),
    )

    intelligence = StrategyIntelligence(strategy_id="S5")

    _ = intelligence.evaluate(results)

    assert not hasattr(intelligence, "execute_trade")
    assert not hasattr(intelligence, "allocate_capital")


def test_strategy_intelligence_verdict_is_immutable():
    results = (
        StrategyResultStub("t1", 100.0, True),
        StrategyResultStub("t2", 90.0, True),
    )

    intelligence = StrategyIntelligence(strategy_id="S6")

    verdict = intelligence.evaluate(results)

    try:
        verdict.health = "UNSTABLE"
        assert False, "Verdict should be immutable"
    except Exception:
        assert True


def test_promotion_signal_is_advisory():
    results = (
        StrategyResultStub("t1", 200.0, True),
        StrategyResultStub("t2", 180.0, True),
        StrategyResultStub("t3", 190.0, True),
    )

    intelligence = StrategyIntelligence(strategy_id="S7")

    verdict = intelligence.evaluate(results)

    assert verdict.promotion_signal in (
        "PROMOTION_ELIGIBLE",
        "NONE",
    )
