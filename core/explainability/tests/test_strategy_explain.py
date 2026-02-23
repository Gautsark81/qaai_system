# core/explainability/tests/test_strategy_explain.py

from core.explainability.strategy import StrategyExplainer
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec


def test_strategy_explanation_contains_core_fields():
    registry = StrategyRegistry()

    spec = StrategySpec(
        name="explain_test",
        alpha_stream="alpha_1",
        timeframe="5m",
        universe=["NIFTY"],
        params={},
    )

    record = registry.register(spec)

    explainer = StrategyExplainer(registry)
    explanation = explainer.explain(record.dna)

    assert explanation["strategy_id"] == record.dna
    assert explanation["state"] == record.state
    assert explanation["alpha_stream"] == "alpha_1"
    assert "health" in explanation
