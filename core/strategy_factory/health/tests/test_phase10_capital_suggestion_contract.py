from core.strategy_factory.health.meta_alpha.capital_suggestion import (
    CapitalSuggestion,
)


def test_capital_suggestion_is_advisory_only():
    suggestion = CapitalSuggestion(
        name="RISK_ON",
        message="Portfolio regime coherent with improving breadth",
        confidence=0.78,
    )

    assert suggestion.advisory_only is True
    assert isinstance(suggestion.message, str)
    assert 0.0 <= suggestion.confidence <= 1.0
