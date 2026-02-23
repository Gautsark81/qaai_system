from core.strategy_factory.health.meta_alpha.ensemble_summary import EnsembleSummary


def test_meta_alpha_has_no_ranking_or_selection():
    forbidden = [
        "rank",
        "select",
        "optimize",
        "allocate",
        "execute",
        "promote",
        "demote",
    ]

    for attr in forbidden:
        assert not hasattr(EnsembleSummary, attr)
