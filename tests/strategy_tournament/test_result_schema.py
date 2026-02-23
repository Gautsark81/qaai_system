from modules.strategy_tournament.result_schema import TradeResult


def test_trade_result_fields():
    t = TradeResult(
        symbol="TEST",
        entry_time="t1",
        exit_time="t2",
        side="BUY",
        qty=1,
        entry_price=100,
        exit_price=101,
        pnl=1,
        reason="test",
    )
    assert t.pnl == 1
