from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote
from core.phase_b.confidence import ConfidenceEngine
from modules.operator_dashboard.service import DashboardService


def test_dashboard_snapshot_contains_strategy_state():
    registry = StrategyRegistry()
    spec = StrategySpec("trend", "trend", "5m", ["NIFTY"], {"len": 50})
    record = registry.register(spec)

    promote(record, "BACKTESTED")
    promote(record, "PAPER")

    dashboard = DashboardService(
        registry=registry,
        confidence_engine=ConfidenceEngine(registry),
    )

    snapshot = dashboard.build_snapshot()

    assert len(snapshot.strategies) == 1
    s = list(snapshot.strategies.values())[0]

    assert s.dna == record.dna
    assert s.name == "trend"
    assert s.state == "PAPER"
    assert s.confidence is not None
