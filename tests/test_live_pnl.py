# tests/test_live_pnl.py
from infra.live_pnl import LivePnL
from providers.dhan_provider import DhanProvider


def test_live_pnl_snapshot():
    dp = DhanProvider(config={"starting_cash": 1000})
    dp.connect()
    # simulate a position
    dp._positions["TST"] = 5
    dp._account_nav = 1000
    # price lookup lambda
    lp = LivePnL(provider=dp, price_lookup=lambda s: 10.0)
    snap = lp.get_snapshot()
    assert snap["account_nav"] == 1000
    assert snap["positions"]["TST"] == 5
    assert snap["unreal_value"]["TST"] == 50.0
