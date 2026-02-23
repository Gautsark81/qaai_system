# core/explainability/tests/test_lifecycle_explain.py

from core.explainability.lifecycle import LifecycleExplainer
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote


def test_lifecycle_explanation_contains_reasoning():
    registry = StrategyRegistry()

    spec = StrategySpec(
        name="explain_test",
        alpha_stream="alpha_x",
        timeframe="5m",
        universe=["NIFTY"],
        params={"x": 1},
    )

    record = registry.register(spec)

    promote(record, "BACKTESTED")
    promote(record, "PAPER")

    explainer = LifecycleExplainer(registry)
    explanation = explainer.explain(record.dna)

    assert explanation["current_state"] == "PAPER"
    assert len(explanation["lifecycle_history"]) == 2
    assert "approved for paper trading" in explanation["explanation"]
