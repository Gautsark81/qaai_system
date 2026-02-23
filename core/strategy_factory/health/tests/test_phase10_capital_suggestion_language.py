from core.strategy_factory.health.meta_alpha.capital_suggestion import (
    CapitalSuggestion,
)


def test_capital_suggestion_language_is_non_mandatory():
    suggestion = CapitalSuggestion(
        name="NEUTRAL",
        message="No strong capital bias detected",
        confidence=0.5,
    )

    forbidden_words = [
        "must",
        "should",
        "force",
        "require",
        "mandate",
    ]

    lower_msg = suggestion.message.lower()
    for word in forbidden_words:
        assert word not in lower_msg
