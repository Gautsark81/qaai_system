from domain.canary.authorized_trade_record import AuthorizedTradeRecord


def test_authorized_trade_record():
    r = AuthorizedTradeRecord("I1", "NIFTY", "BUY", 20000)
    assert r.authorized_capital == 20000
