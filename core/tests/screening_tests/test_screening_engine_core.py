from core.screening.engine import ScreeningEngine
from core.screening.rules import LiquidityRule, TrendRule
from core.screening.models import MarketSnapshot


def test_engine_pass():
    engine = ScreeningEngine([
        LiquidityRule(500_000),
        TrendRule(0.5),
    ])

    snap = MarketSnapshot("A", 100, 1e6, 2, 0.2, 0.8)
    result = engine.screen(snap)

    assert result.passed is True
    assert result.failed_rules == []
