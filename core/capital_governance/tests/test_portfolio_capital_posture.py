import inspect
from core.capital_governance import (
    StrategyCapitalView,
    build_portfolio_capital_posture,
)


def test_portfolio_capital_aggregation():
    views = [
        StrategyCapitalView("s1", 1000, 800, 0.05),
        StrategyCapitalView("s2", 2000, 1500, 0.10),
    ]

    snapshot = build_portfolio_capital_posture(views)

    posture = snapshot.posture
    assert posture.total_allocated == 3000
    assert posture.total_utilized == 2300
    assert posture.max_drawdown == 0.10
    assert set(posture.per_strategy.keys()) == {"s1", "s2"}


def test_builder_is_deterministic():
    view = StrategyCapitalView("s1", 1000, 900, 0.02)

    r1 = build_portfolio_capital_posture([view])
    r2 = build_portfolio_capital_posture([view])

    assert r1.posture == r2.posture
    assert r1.snapshot_version == r2.snapshot_version


def test_no_execution_authority_present():
    source = inspect.getsource(build_portfolio_capital_posture).lower()

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "call(",
        "while",
        "for ",
    ]

    for word in forbidden:
        assert word not in source
