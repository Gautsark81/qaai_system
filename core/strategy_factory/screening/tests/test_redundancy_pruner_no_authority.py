from core.strategy_factory.screening.redundancy_pruner import RedundancyPruner


def test_pruner_has_no_authority():
    pruner = RedundancyPruner()

    forbidden = [
        "allocate",
        "promote",
        "execute",
        "approve",
        "mutate",
    ]

    for method in forbidden:
        assert not hasattr(pruner, method)