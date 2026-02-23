from core.screening.models import MarketSnapshot
from core.screening.rules import LiquidityRule, VolatilityRule, TrendRule


def snapshot(**kw):
    return MarketSnapshot("A", 100, 1e6, 2.0, 0.3, 0.8)


def test_liquidity_rule():
    rule = LiquidityRule(min_volume=500_000)
    assert rule.evaluate(snapshot())


def test_volatility_rule_fail():
    rule = VolatilityRule(max_volatility=0.2)
    assert not rule.evaluate(snapshot())


def test_trend_rule_pass():
    rule = TrendRule(min_trend=0.7)
    assert rule.evaluate(snapshot())
