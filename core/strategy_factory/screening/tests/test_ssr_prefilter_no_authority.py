from core.strategy_factory.screening.ssr_prefilter import SSRPreFilter


def test_ssr_prefilter_has_no_authority():
    prefilter = SSRPreFilter()

    forbidden = [
        "allocate",
        "promote",
        "execute",
        "approve",
        "mutate",
    ]

    for method in forbidden:
        assert not hasattr(prefilter, method)