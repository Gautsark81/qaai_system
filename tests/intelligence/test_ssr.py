from intelligence.ssr.ssr_calculator import SSRCalculator
from intelligence.ssr.ssr_types import TradeOutcome


def test_ssr_basic():
    trades = [TradeOutcome(1), TradeOutcome(-1), TradeOutcome(2)]
    res = SSRCalculator.compute(trades)

    assert res.total_trades == 3
    assert res.successful_trades == 2
    assert res.ssr == 0.6667
    assert res.valid is False  # < MIN_TRADES


def test_ssr_empty():
    res = SSRCalculator.compute([])
    assert res.total_trades == 0
    assert res.successful_trades == 0
    assert res.ssr == 0.0
