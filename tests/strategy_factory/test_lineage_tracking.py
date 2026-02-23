from qaai_system.strategy_factory.evolution.lineage import spawn_lineage


def test_lineage_generation_increment():
    parent = {"strategy_id": "s1", "generation": 1}
    child = spawn_lineage(parent, "test")

    assert child["generation"] == 2
    assert child["parent"] == "s1"
