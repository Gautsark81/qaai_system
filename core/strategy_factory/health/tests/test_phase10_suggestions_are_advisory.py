from core.strategy_factory.health.meta_alpha.suggestion import MetaAlphaSuggestion


def test_meta_alpha_suggestion_is_advisory():
    suggestion = MetaAlphaSuggestion(
        message="Portfolio breadth improving; volatility elevated",
        confidence=0.74,
    )

    assert suggestion.advisory_only is True
    assert isinstance(suggestion.message, str)
