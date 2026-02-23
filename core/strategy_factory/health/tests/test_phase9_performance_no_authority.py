from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.strategy_health_report import StrategyHealthReport


def test_performance_intelligence_has_no_authority():
    snapshot = StrategyHealthSnapshot(
        health_score=0.55,
        confidence=0.7,
        decay_risk=0.2,
        ssr=0.5,
        max_drawdown=0.15,
        total_trades=150,
    )

    report = StrategyHealthReport.__new__(StrategyHealthReport)

    forbidden = [
        "execute",
        "allocate_capital",
        "promote",
        "demote",
        "block",
    ]

    for obj in (snapshot, report):
        for attr in forbidden:
            assert not hasattr(obj, attr)
