from core.strategy_factory.health.strategy_health_report import StrategyHealthReport


def test_failure_patterns_have_no_authority_methods():
    report = StrategyHealthReport.__new__(StrategyHealthReport)

    forbidden_attrs = [
        "execute",
        "allocate_capital",
        "promote",
        "demote",
        "block",
    ]

    for attr in forbidden_attrs:
        assert not hasattr(report, attr)
