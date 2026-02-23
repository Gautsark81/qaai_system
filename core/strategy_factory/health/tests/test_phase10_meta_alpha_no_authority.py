from core.strategy_factory.health.meta_alpha.ensemble_summary import EnsembleSummary
from core.strategy_factory.health.meta_alpha.suggestion import MetaAlphaSuggestion


def test_meta_alpha_objects_have_no_authority():
    forbidden = [
        "execute",
        "allocate_capital",
        "override_risk",
        "force_promote",
        "force_demote",
        "gate",
    ]

    for cls in (EnsembleSummary, MetaAlphaSuggestion):
        for attr in forbidden:
            assert not hasattr(cls, attr)
