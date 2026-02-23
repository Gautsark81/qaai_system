def test_end_to_end_generation():
    from core.strategy_factory.generation import generate_strategies

    records = generate_strategies(seed=42, population_size=10)

    assert records
    for r in records:
        assert r.state == "GENERATED"
