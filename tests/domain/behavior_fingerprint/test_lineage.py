from datetime import datetime
from domain.behavior_fingerprint.lineage import LineageNode, StrategyLineage


def test_strategy_lineage_structure():
    node = LineageNode(
        strategy_id="s1",
        fingerprint_version=1,
        mutation_type="param_tune",
        created_ts=datetime.utcnow(),
    )

    lineage = StrategyLineage(
        strategy_id="s2",
        root_strategy_id="s1",
        ancestors=[node],
        descendants=[],
    )

    assert lineage.root_strategy_id == "s1"
