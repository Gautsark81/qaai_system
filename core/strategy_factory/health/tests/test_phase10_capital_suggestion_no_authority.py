from core.strategy_factory.health.meta_alpha.capital_suggestion import (
    CapitalSuggestion,
)


def test_capital_suggestion_has_no_authority():
    forbidden = [
        "allocate",
        "set_capital",
        "override_capital",
        "throttle",
        "execute",
        "promote",
        "demote",
    ]

    for attr in forbidden:
        assert not hasattr(CapitalSuggestion, attr)
