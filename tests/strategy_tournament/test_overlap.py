# tests/strategy_tournament/test_overlap.py

from modules.strategy_tournament.overlap import trade_overlap_ratio
from modules.strategy_tournament.result_schema import TradeResult


def _trade(symbol, et, xt):
    return TradeResult(
        symbol=symbol,
        entry_time=et,
        exit_time=xt,
        side="BUY",
        qty=1,
        entry_price=100,
        exit_price=101,
        pnl=1,
        reason="test",
    )


def test_no_overlap():
    a = [_trade("A", "t1", "t2")]
    b = [_trade("B", "t1", "t2")]
    assert trade_overlap_ratio(a, b) == 0.0


def test_full_overlap():
    t = _trade("A", "t1", "t2")
    a = [t]
    b = [t]
    assert trade_overlap_ratio(a, b) == 1.0


def test_partial_overlap():
    a = [
        _trade("A", "t1", "t2"),
        _trade("A", "t3", "t4"),
    ]
    b = [
        _trade("A", "t1", "t2"),
        _trade("B", "t5", "t6"),
    ]
    ratio = trade_overlap_ratio(a, b)
    assert 0.0 < ratio < 1.0


def test_empty_inputs():
    assert trade_overlap_ratio([], []) == 0.0
    assert trade_overlap_ratio([], [_trade("A", "t1", "t2")]) == 0.0
