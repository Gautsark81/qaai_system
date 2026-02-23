from core.strategy_factory.ensemble import EnsembleRegistry


def test_registry_filters_and_sorts():
    data = [
        {"strategy_id": "B", "ssr": 82},
        {"strategy_id": "A", "ssr": 91},
        {"strategy_id": "C", "ssr": 75},
    ]

    result = EnsembleRegistry.load(data)

    assert len(result) == 2
    assert result[0].strategy_id == "A"
    assert result[1].strategy_id == "B"